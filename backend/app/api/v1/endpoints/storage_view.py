"""Storage streaming and download endpoint supporting byte ranges."""
import mimetypes
import os
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from app.core.config import settings
from app.core.errors import NotFoundError
from app.observability.logger import logger

router = APIRouter()


@router.get(
    "/storage/{file_path:path}",
    summary="Download or stream an artifact file with Range request support"
)
async def get_storage_artifact(file_path: str, request: Request):
    """Streams video or audio with HTTP 206 Partial Content range support."""
    clean = file_path.lstrip("/\\")
    full_path = (Path(settings.STORAGE_LOCAL_DIR).resolve() / clean).resolve()

    if not full_path.exists() or not full_path.is_file():
        raise NotFoundError(f"Artifact '{file_path}' not found.", code="ARTIFACT_NOT_FOUND")

    mime_type, _ = mimetypes.guess_type(str(full_path))
    if not mime_type:
        mime_type = "application/octet-stream"

    file_size = full_path.stat().st_size
    range_header = request.headers.get("range")

    # If range header requested (standard for HTML5 video seeking)
    if range_header and range_header.startswith("bytes="):
        ranges = range_header.replace("bytes=", "").split("-")
        start = int(ranges[0]) if ranges[0] else 0
        end = int(ranges[1]) if len(ranges) > 1 and ranges[1] else file_size - 1

        if start >= file_size or end >= file_size or start > end:
            return Response(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                headers={"Content-Range": f"bytes */{file_size}"}
            )

        content_length = (end - start) + 1

        def iter_file(chunk_size: int = 65536):
            with open(full_path, "rb") as f:
                f.seek(start)
                bytes_left = content_length
                while bytes_left > 0:
                    read_len = min(chunk_size, bytes_left)
                    data = f.read(read_len)
                    if not data:
                        break
                    bytes_left -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": mime_type,
            "Access-Control-Allow-Origin": "*",
        }
        return StreamingResponse(iter_file(), status_code=status.HTTP_206_PARTIAL_CONTENT, headers=headers)

    # Standard full file response
    return FileResponse(
        full_path,
        media_type=mime_type,
        headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"}
    )
