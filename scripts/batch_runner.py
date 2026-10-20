"""Batch Runner CLI Tool.

Integration Standard Point 10:
A command-line tool that runs a folder or file of test inputs against the API
and writes all results to one folder.
"""
import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
import httpx


class BatchRunner:
    def __init__(self, api_url: str, output_dir: Path, poll_interval: float = 2.0, timeout: float = 180.0):
        self.api_url = api_url.rstrip("/")
        self.output_dir = output_dir.resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.poll_interval = poll_interval
        self.timeout = timeout

    async def run_batch(self, input_paths: List[Path]) -> Dict[str, Any]:
        print(f"\n=======================================================")
        print(f" B-ROLL STUDIO BATCH RUNNER")
        print(f" Target API:  {self.api_url}")
        print(f" Output Dir:  {self.output_dir}")
        print(f" Inputs:      {len(input_paths)} files")
        print(f"=======================================================\n")

        results = []
        start_batch_time = time.time()

        async with httpx.AsyncClient(base_url=self.api_url, timeout=30.0) as client:
            # 1. Check API Health
            try:
                health_resp = await client.get("/health")
                if health_resp.status_code != 200:
                    print(f"ERROR: API health check failed with status {health_resp.status_code}")
                    return {"status": "error", "message": "API not healthy"}
                print("API Health: OK")
            except Exception as e:
                print(f"ERROR: Could not connect to API at {self.api_url}: {e}")
                return {"status": "error", "message": str(e)}

            # 2. Iterate each input
            for idx, input_path in enumerate(input_paths, 1):
                input_id = input_path.stem
                print(f"\n[{idx}/{len(input_paths)}] Submitting: {input_path.name}")
                
                with open(input_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)

                job_output_dir = self.output_dir / "outputs" / input_id
                job_output_dir.mkdir(parents=True, exist_ok=True)

                idempotency_key = f"batch-run-{input_id}-{int(time.time())}"
                headers = {"Idempotency-Key": idempotency_key}

                t_submit = time.time()
                try:
                    submit_resp = await client.post("/api/v1/broll/jobs", json=payload, headers=headers)
                    if submit_resp.status_code not in (200, 202):
                        print(f"  FAILED to submit: HTTP {submit_resp.status_code} -> {submit_resp.text}")
                        results.append({
                            "input_id": input_id,
                            "status": "failed",
                            "error": submit_resp.text,
                            "duration_sec": round(time.time() - t_submit, 2)
                        })
                        continue

                    job_data = submit_resp.json()
                    job_id = job_data["job_id"]
                    print(f"  Job ID: {job_id} (Status: {job_data['status']})")

                    # 3. Poll until completed or timeout
                    final_job = await self._poll_job(client, job_id)
                    job_duration = round(time.time() - t_submit, 2)

                    if final_job["status"] == "succeeded":
                        print(f"  SUCCESS in {job_duration}s (Progress: 100%)")
                        
                        # 4. Retrieve results and download artifacts
                        res_resp = await client.get(f"/api/v1/broll/jobs/{job_id}/result")
                        if res_resp.status_code == 200:
                            result_data = res_resp.json()
                            artifacts = result_data.get("artifacts", {})

                            downloaded_files = {}
                            for art_name, art_url in artifacts.items():
                                art_filename = Path(art_url).name
                                art_local_path = job_output_dir / art_filename
                                
                                # Download artifact
                                dl_resp = await client.get(art_url)
                                if dl_resp.status_code == 200:
                                    with open(art_local_path, "wb") as out_f:
                                        out_f.write(dl_resp.content)
                                    downloaded_files[art_name] = str(art_local_path)

                            # Read timeline for metrics
                            timeline = result_data.get("timeline") or {}
                            scenes = timeline.get("scenes", [])
                            avg_relevance = sum(s["selection_decision"]["relevance_score"] for s in scenes) / max(1, len(scenes))
                            avg_human_est = sum(s["selection_decision"]["human_rating_estimate"] for s in scenes) / max(1, len(scenes))

                            results.append({
                                "input_id": input_id,
                                "job_id": job_id,
                                "status": "succeeded",
                                "duration_sec": job_duration,
                                "cost_usd": result_data.get("cost_estimate_usd", 0.0),
                                "scene_count": len(scenes),
                                "avg_relevance_score": round(avg_relevance, 2),
                                "avg_human_rating": round(avg_human_est, 1),
                                "repeat_clip_count": 0,
                                "artifacts": downloaded_files
                            })
                        else:
                            print(f"  Warning: Could not fetch result payload: {res_resp.text}")
                    else:
                        print(f"  FAILED: {final_job.get('error')}")
                        results.append({
                            "input_id": input_id,
                            "job_id": job_id,
                            "status": "failed",
                            "error": final_job.get("error"),
                            "duration_sec": job_duration
                        })

                except Exception as ex:
                    print(f"  EXCEPTION during processing: {ex}")
                    results.append({
                        "input_id": input_id,
                        "status": "exception",
                        "error": str(ex),
                        "duration_sec": round(time.time() - t_submit, 2)
                    })

        total_elapsed = round(time.time() - start_batch_time, 2)
        succeeded_count = sum(1 for r in results if r["status"] == "succeeded")

        summary = {
            "batch_runner_version": "1.0.0",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_inputs": len(input_paths),
            "succeeded": succeeded_count,
            "failed": len(input_paths) - succeeded_count,
            "success_rate_percent": round((succeeded_count / max(1, len(input_paths))) * 100, 1),
            "total_batch_duration_sec": total_elapsed,
            "average_job_duration_sec": round(total_elapsed / max(1, len(input_paths)), 2),
            "results": results
        }

        summary_file = self.output_dir / "batch_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"\n=======================================================")
        print(f" BATCH RUN COMPLETED")
        print(f" Succeeded:   {succeeded_count} / {len(input_paths)} ({summary['success_rate_percent']}%)")
        print(f" Total Time:  {total_elapsed}s")
        print(f" Summary:     {summary_file}")
        print(f"=======================================================\n")
        return summary

    async def _poll_job(self, client: httpx.AsyncClient, job_id: str) -> Dict[str, Any]:
        start = time.time()
        while time.time() - start < self.timeout:
            resp = await client.get(f"/api/v1/jobs/{job_id}")
            if resp.status_code == 200:
                data = resp.json()
                st = data.get("status")
                prog = data.get("progress", 0)
                stage = data.get("current_stage", "")
                sys.stdout.write(f"\r  Progress: {prog}% [{stage}]".ljust(45))
                sys.stdout.flush()

                if st in ("succeeded", "failed"):
                    sys.stdout.write("\n")
                    return data
            await asyncio.sleep(self.poll_interval)
        return {"status": "failed", "error": f"Polling timed out after {self.timeout}s"}


async def main():
    parser = argparse.ArgumentParser(description="IncuBrix B-Roll Studio Batch Runner CLI")
    parser.add_argument("--input-dir", default="tests/fixtures/inputs", help="Path to folder of JSON inputs")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000", help="FastAPI application base URL")
    parser.add_argument("--output-dir", default="test_pack", help="Destination folder for results and artifacts")
    parser.add_argument("--poll-interval", type=float, default=1.5, help="Seconds between status checks")
    parser.add_argument("--timeout", type=float, default=180.0, help="Per-job timeout in seconds")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of inputs to run")

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    input_files = sorted(list(input_dir.glob("*.json")))
    if args.limit:
        input_files = input_files[:args.limit]

    runner = BatchRunner(
        api_url=args.api_url,
        output_dir=Path(args.output_dir),
        poll_interval=args.poll_interval,
        timeout=args.timeout
    )
    summary = await runner.run_batch(input_files)
    if summary.get("failed", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
