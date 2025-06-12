from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import engine, SessionLocal
from database import Base
import models, schemas
from typing import Optional

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/create_user')
def register_user(request: schemas.User, db: Session = Depends(get_db)):
    existing_email = db.query(models.User).filter(func.lower(models.User.email) == request.email.lower()).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_name = db.query(models.User).filter(models.User.name == request.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    new_user = models.User(name=request.name, email=request.email, password=request.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

'''getting all the registered user as the api'''
@app.get('/registered_user')
def show_users(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.post('/add_product')
def add_product(request: schemas.Product, db:Session = Depends(get_db)):
    print("Received request:", request.dict())
    
    existing_product = db.query(models.Product).filter(
        func.lower(models.Product.name) == request.name.lower()
    ).first()

    print("Existing product found?", existing_product is not None)

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already exists"
        )

    new_product = models.Product(
        name=request.name,
        description=request.description,
        price=request.price,
        is_available=request.is_available
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product has been added", "product": new_product}

@app.get('/all_products')
def all_products(db:Session = Depends(get_db)):
    product = db.query(models.Product).all()
    return {"Message": "Showing all the products from database", 'product': product}

@app.get('/product/{product_id}')
def product_fetch(product_id: int, product_name: Optional[str] = None,db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id and models.Product.name == product_name).first()
    if not product:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    #return {"Message" : "details of product of ", "product" : product_id}
    return product
