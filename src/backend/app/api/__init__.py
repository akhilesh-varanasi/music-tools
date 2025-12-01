from fastapi import APIRouter
from app.core.config import settings
from app.api.v1 import example

api_router = APIRouter()
api_router.include_router(example.router, prefix=settings.api_v1_prefix)
