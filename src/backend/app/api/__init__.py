from fastapi import APIRouter
from app.core.config import settings
from app.api.v1 import album_art, yt2mp3

api_router = APIRouter()
api_router.include_router(album_art.router, prefix=settings.api_v1_prefix)
api_router.include_router(yt2mp3.router, prefix=settings.api_v1_prefix)
