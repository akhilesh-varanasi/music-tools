# app/api/v1/yt2mp3.py
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.yt2mp3_service import batch_download_audio

router = APIRouter(prefix="/yt2mp3", tags=["yt2mp3"])


class Yt2Mp3Request(BaseModel):
    urls: List[str]
    output_dir: str
    browser: str | None = None


class Yt2Mp3TrackResult(BaseModel):
    url: str
    video_id: str | None = None
    title: str | None = None
    output_path: str | None = None
    success: bool
    error: str | None = None


class Yt2Mp3Response(BaseModel):
    results: List[Yt2Mp3TrackResult]
    total_tracks: int
    total_success: int
    total_failed: int


@router.post("/batch", response_model=Yt2Mp3Response)
async def yt2mp3_batch(body: Yt2Mp3Request):
    print("hello")
    urls = [u.strip() for u in body.urls if u and u.strip()]
    print(f"found urls: {urls}")
    if not urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    output_dir = Path(body.output_dir).expanduser()

    try:
        raw_results = batch_download_audio(urls, output_dir)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results = [Yt2Mp3TrackResult(**r) for r in raw_results]
    total_tracks = len(results)
    total_success = sum(1 for r in results if r.success)
    total_failed = total_tracks - total_success

    return Yt2Mp3Response(
        results=results,
        total_tracks=total_tracks,
        total_success=total_success,
        total_failed=total_failed,
    )
