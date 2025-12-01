from fastapi import APIRouter
from typing import List

from app.models.example_model import ExampleItem
from app.services.example_service import list_example_items

router = APIRouter(prefix="/example", tags=["example"])


@router.get("/", response_model=List[ExampleItem])
async def get_items() -> List[ExampleItem]:
    return list_example_items()