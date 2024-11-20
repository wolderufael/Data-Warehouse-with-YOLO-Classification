from sqlalchemy import Column, Integer, String,ARRAY,Float,MetaData,Table
from database import Base,engine

#  Define metadata
metadata = MetaData()

class Item(Base):
    __tablename__ = "product_classification"
    # __table_args__ = {'autoload': True}
        

    image_name = Column(String, primary_key=True, index=True)
    product_category=Column(String, index=True) # category based on yolo classification	

  
