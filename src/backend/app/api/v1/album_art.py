# app/api/v1/album_art.py
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.album_art import (
    gather_batch_paths,
    batch_replace_album_art_in_place,
)
import io

router = APIRouter(prefix="/album-art", tags=["album-art"])

class BatchPathsRequest(BaseModel):
    # Each entry may be:
    #   - a file path
    #   - a directory path
    song_paths: List[str] = []
    image_paths: List[str] = []


class BatchResultItem(BaseModel):
    song_path: str
    image_used: str | None = None
    success: bool
    error: str | None = None


class BatchPathsResponse(BaseModel):
    results: List[BatchResultItem]
    total_songs: int
    total_success: int
    total_failed: int


@router.post("/batch-paths", response_model=BatchPathsResponse)
async def replace_batch_album_art_paths(body: BatchPathsRequest):
    try:
        song_paths, image_paths = gather_batch_paths(
            song_paths=body.song_paths,
            image_paths=body.image_paths,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        raw_results = batch_replace_album_art_in_place(song_paths, image_paths)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results = [BatchResultItem(**r) for r in raw_results]
    total_songs = len(results)
    total_success = sum(1 for r in results if r.success)
    total_failed = total_songs - total_success

    return BatchPathsResponse(
        results=results,
        total_songs=total_songs,
        total_success=total_success,
        total_failed=total_failed,
    )
