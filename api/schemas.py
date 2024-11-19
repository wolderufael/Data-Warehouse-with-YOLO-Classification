from pydantic import BaseModel
from typing import List, Optional,Dict

class ItemCreate(BaseModel):
    image_name: str
    product_category: str


# Define the schema for reading an item (with id)
class Item(BaseModel):
    image_name: str  # Primary key field
    product_category: str


class RenderResponse(BaseModel):
    image_name: str
    product_category: str

    class Config:
        orm_mode = True  # Allows Pydantic to work with ORM models
