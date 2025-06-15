from backend.database import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

class Product(Base):
    __tablename__ = "products"   # table name in DB

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Integer)
    is_available = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    product = relationship("Product")