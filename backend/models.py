from database import Base
from sqlalchemy import Column, String, Integer, Boolean

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    price = Column(Integer)
    is_available = Column(Boolean)