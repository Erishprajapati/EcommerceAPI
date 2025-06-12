from pydantic import BaseModel
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

class Product(BaseModel):
    name:str
    description:str
    price:int
    is_available:bool
