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
        from_attributes = True  # allows loading from ORM objects