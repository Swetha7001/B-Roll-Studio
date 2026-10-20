"""Dual-backend Storage Manager (Local Directory & S3 / MinIO).

Integration Standard Point 7:
Files in (uploads & safe URLs) -> Files out (S3 / MinIO compatible storage).
"""
import io
import ipaddress
import os
import shutil
import socket
import urllib.parse
from pathlib import Path
from typing import BinaryIO, Optional, Tuple, Union
import httpx

from app.core.config import settings
from app.core.errors import AppError, NotFoundError, SsrfBlockedError
from app.observability.logger import logger


class StorageManager:
    """Manages file storage locally or in MinIO/S3 object storage."""
    def __init__(self):
        self.backend = settings.STORAGE_BACKEND.lower()
        self.local_dir = Path(settings.STORAGE_LOCAL_DIR).resolve()
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self._minio_client = None

        if self.backend == "s3":
            try:
                from minio import Minio
                self._minio_client = Minio(
                    settings.MINIO_ENDPOINT,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_SECURE,
                )
                # Ensure bucket exists
                if not self._minio_client.bucket_exists(settings.MINIO_BUCKET):
                    self._minio_client.make_bucket(settings.MINIO_BUCKET)
                logger.info(f"Connected to MinIO/S3 bucket '{settings.MINIO_BUCKET}'")
            except Exception as e:
                logger.warning(f"Could not initialize MinIO client ({e}). Falling back to local storage.")
                self.backend = "local"

    def get_job_dir(self, job_id: str) -> Path:
        """Returns the local directory path for a job's artifacts."""
        p = self.local_dir / job_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def put_file(
        self,
        relative_path: str,
        file_data: Union[bytes, BinaryIO, str, Path],
        content_type: str = "application/octet-stream"
    ) -> str:
        """Stores a file and returns its access URL/path."""
        clean_path = relative_path.lstrip("/\\")

        if self.backend == "s3" and self._minio_client:
            try:
                if isinstance(file_data, (str, Path)) and os.path.exists(str(file_data)):
                    self._minio_client.fput_object(
                        settings.MINIO_BUCKET,
                        clean_path,
                        str(file_data),
                        content_type=content_type
                    )
                elif isinstance(file_data, bytes):
                    data_stream = io.BytesIO(file_data)
                    self._minio_client.put_object(
                        settings.MINIO_BUCKET,
                        clean_path,
                        data_stream,
                        length=len(file_data),
                        content_type=content_type
                    )
                else:
                    # Seekable stream
                    file_data.seek(0, os.SEEK_END)
                    size = file_data.tell()
                    file_data.seek(0)
                    self._minio_client.put_object(
                        settings.MINIO_BUCKET,
                        clean_path,
                        file_data,
                        length=size,
                        content_type=content_type
                    )
                # Return download endpoint
                return f"/api/v1/storage/{clean_path}"
            except Exception as e:
                logger.error(f"S3 upload failed for {clean_path}: {e}")
                # Fallback to local
                pass

        # Local storage fallback
        dest_path = self.local_dir / clean_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(file_data, (str, Path)) and os.path.exists(str(file_data)):
            shutil.copy2(str(file_data), str(dest_path))
        elif isinstance(file_data, bytes):
            with open(dest_path, "wb") as f:
                f.write(file_data)
        elif hasattr(file_data, "read"):
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file_data, f)
        else:
            raise ValueError(f"Unsupported file_data type: {type(file_data)}")

        return f"/api/v1/storage/{clean_path}"

    def get_local_path(self, relative_path: str) -> Path:
        """Returns the local filesystem path if available, or downloads from S3."""
        clean_path = relative_path.lstrip("/\\")
        local_dest = self.local_dir / clean_path

        if local_dest.exists():
            return local_dest

        if self.backend == "s3" and self._minio_client:
            try:
                local_dest.parent.mkdir(parents=True, exist_ok=True)
                self._minio_client.fget_object(
                    settings.MINIO_BUCKET,
                    clean_path,
                    str(local_dest)
                )
                return local_dest
            except Exception as e:
                logger.error(f"Failed to fetch {clean_path} from S3: {e}")

        raise FileNotFoundError(f"Artifact {clean_path} not found")

    def exists(self, relative_path: str) -> bool:
        clean_path = relative_path.lstrip("/\\")
        if (self.local_dir / clean_path).exists():
            return True
        if self.backend == "s3" and self._minio_client:
            try:
                self._minio_client.stat_object(settings.MINIO_BUCKET, clean_path)
                return True
            except Exception:
                return False
        return False


def validate_and_download_url(
    url: str,
    target_path: Path,
    max_size_bytes: int = 100 * 1024 * 1024,
    timeout_sec: float = 15.0
) -> Path:
    """Safely downloads a remote media URL with SSRF protection."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SsrfBlockedError(f"Scheme '{parsed.scheme}' not allowed. Only HTTP/HTTPS supported.")

    hostname = parsed.hostname
    if not hostname:
        raise SsrfBlockedError("Missing hostname in target URL")

    # SSRF: Resolve IP and reject private / loopback / link-local addresses
    try:
        ip_addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise SsrfBlockedError(f"Could not resolve host '{hostname}': {e}")

    for addr in ip_addresses:
        ip_str = addr[4][0]
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            raise SsrfBlockedError(f"Target host '{hostname}' resolves to restricted IP {ip_str}")

    # Stream download
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=timeout_sec, follow_redirects=True) as client:
        with client.stream("GET", url) as response:
            if response.status_code != 200:
                raise AppError(
                    code="REMOTE_FETCH_FAILED",
                    message=f"Remote server returned HTTP {response.status_code}",
                    status_code=400
                )
            
            bytes_downloaded = 0
            with open(target_path, "wb") as out_file:
                for chunk in response.iter_bytes(chunk_size=65536):
                    bytes_downloaded += len(chunk)
                    if bytes_downloaded > max_size_bytes:
                        raise AppError(
                            code="FILE_TOO_LARGE",
                            message=f"Remote media exceeds size limit of {max_size_bytes / (1024*1024):.1f}MB",
                            status_code=400
                        )
                    out_file.write(chunk)

    return target_path


storage = StorageManager()
