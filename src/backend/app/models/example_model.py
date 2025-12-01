from pydantic import BaseModel

class ExampleItem(BaseModel):
    id: int
    name: str
    description: str | None = None