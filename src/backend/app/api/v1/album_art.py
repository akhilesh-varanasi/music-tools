# app/api/v1/album_art.py
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.album_art import replace_album_art_in_place, replace_album_art_bytes
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
import io

router = APIRouter(prefix="/album-art", tags=["album-art"])


# existing upload-based endpoint (browser-friendly)
@router.post("/single")
async def replace_single_album_art(
    song: UploadFile = File(...),
    image: UploadFile = File(...),
):
    song_filename = song.filename or "song.mp3"
    image_filename = image.filename or "cover.jpg"

    if not song_filename.lower().endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only .mp3 files are supported")

    song_bytes = await song.read()
    image_bytes = await image.read()

    try:
        updated_bytes, output_name = replace_album_art_bytes(
            mp3_bytes=song_bytes,
            mp3_filename=song_filename,
            image_bytes=image_bytes,
            image_filename=image_filename,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update album art")

    return StreamingResponse(
        io.BytesIO(updated_bytes),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{output_name}"'
        },
    )


class SinglePathRequest(BaseModel):
    mp3_path: str
    image_path: str

@router.post("/single-path")
async def replace_single_album_art_path(body: SinglePathRequest):
    mp3_path = Path(body.mp3_path).expanduser()
    image_path = Path(body.image_path).expanduser()

    try:
        replace_album_art_in_place(mp3_path, image_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update album art")

    return {"status": "ok", "mp3_path": str(mp3_path)}
