from pydantic import BaseModel
from typing import Optional
# class Book(BaseModel):
#     title:str
#     description:str

# class showBook(Book):
#     class Config():
#         orm_mode = True


class User(BaseModel):
    name:str
    email:str
    password:str

class Login(BaseModel):
    email:str
    password:str

class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    is_available: bool
    image_url: Optional[str] = None

    class Config:
        from_attributes = True  # allows loading from ORM 
        
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartItemWithProduct(BaseModel):
    id: int
    quantity: int
    product: Product

    class Config:
        from_attributes = True