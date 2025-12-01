from fastapi import APIRouter
from app.core.config import settings
from app.api.v1 import album_art

api_router = APIRouter()
api_router.include_router(album_art.router, prefix=settings.api_v1_prefix)
