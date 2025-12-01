from typing import List
from app.models.example_model import ExampleItem

def list_example_items() -> List[ExampleItem]:
    return [
        ExampleItem(id=1, name="First item", description="Hello from backend"),
        ExampleItem(id=2, name="Second item"),
    ]