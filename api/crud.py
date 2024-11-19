from sqlalchemy.orm import Session
import models, schemas

# Function to create a new item in the database
# def create_item(db: Session, item: schemas.ItemCreate):
#     # Create an instance of the Item model by passing in the data from the schema
#     db_item = models.Item(image_name=item.image_name, product_category=item.product_category)
    
#     # Add the new item to the session
#     db.add(db_item)
    
#     # Commit the session to save the item to the database
#     db.commit()
    
#     # Refresh the db_item to reflect the latest state from the database (e.g., if there are any auto-generated fields)
#     db.refresh(db_item)
    
#     # Return the newly created item
#     return db_item

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())  # Create Item object from schema
    db.add(db_item)  # Add the item to the session
    db.commit()  # Commit the transaction
    db.refresh(db_item)  # Refresh to get the updated object with any DB-generated fields (like ID)
    return db_item  # Return the created item

# Function to get an item by product_category
def get_item_by_product_category(db: Session, product_category: str, skip: int = 0, limit: int = 10):
    return db.query(models.Item).filter(models.Item.product_category == product_category).offset(skip).limit(limit).all()

# Function to get an item by image_name
def get_item_by_image_name(db: Session, image_name: str):
    return db.query(models.Item).filter(models.Item.image_name == image_name).first()