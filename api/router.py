from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
from typing import List, Optional,Dict
from fastapi import HTTPException

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Create Item endpoint
# @router.post("/items/", response_model=schemas.Item)
# def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
#     # Call the create_item function in CRUD to add the new item
#     db_item = crud.create_item(db=db, item=item)
#     return db_item

@router.post("/items/", response_model=schemas.Item)
def create_item(image_name: str, product_category: str, db: Session = Depends(get_db)):
    db_item = crud.create_item(db=db, item=schemas.ItemCreate(image_name=image_name, product_category=product_category))
    return db_item

# Get items by product_category
@router.get("/items/category/{product_category}", response_model=List[schemas.Item])
def get_items_by_category(product_category: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_item_by_product_category(db=db, product_category=product_category, skip=skip, limit=limit)

# Get item by image_name
@router.get("/items/image/{image_name}", response_model=schemas.Item)
def get_item_by_image_name(image_name: str, db: Session = Depends(get_db)):
    item = crud.get_item_by_image_name(db=db, image_name=image_name)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
