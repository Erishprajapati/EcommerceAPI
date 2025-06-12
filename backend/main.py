from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import engine, SessionLocal
from database import Base
import models, schemas, hashing
from typing import Optional
from sqlalchemy.exc import IntegrityError

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
    try:
        # Check for existing email (case-insensitive)
        existing_email = db.query(models.User).filter(
            func.lower(models.User.email) == request.email.lower()
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check for existing name (case-insensitive)
        existing_name = db.query(models.User).filter(
            func.lower(models.User.name) == request.name.lower()
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        new_user = models.User(name=request.name, email=request.email, password=hashing.Hash.bcrypt(request.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation. User might already exist."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

'''getting all the registered user as the api'''
@app.get('/registered_user')
def show_users(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.put('/user/{user_id}/update')
def update_user(user_id:int, request: schemas.User, db:Session = Depends(get_db)):
    updated_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'User with user_id{user_id} not found.')
    updated_user.name = request.name
    updated_user.email = request.email
    updated_user.password = hashing.Hash.bcrypt(request.password)
    db.commit()
    db.refresh(updated_user)
    return {"Message" : "User updated with information",'Information': updated_user}
    
@app.delete('/user/delete/{user_id}')
def delete_user(user_id:int, db:Session = Depends(get_db))->None:
    result = db.query(models.User).filter(models.User.id == user_id).delete(synchronize_session=False)
    db.commit()
    if result == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User with {user_id} not found")
    return {"message" : "User deleted succesfully"}

@app.post('/add_product')
def add_product(request: schemas.Product, db:Session = Depends(get_db)):
    try:
        print("Received request:", request.dict())
        
        # Check for existing product (case-insensitive)
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
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation. Product might already exist."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@app.get('/all_products')
def all_products(db:Session = Depends(get_db)):
    product = db.query(models.Product).all()
    return {"Message": "Showing all the products from database", 'product': product}

@app.delete('/product/{product_id}/delete')
def delete_product(product_id:int, db:Session = Depends(get_db)):
    result = db.query(models.Product).filter(models.Product.id == product_id).delete(synchronize_session=False)
    db.commit()
    if result == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Product with id {product_id} not found")
    return "Product deletion succesful"

@app.get('/product/{product_id}')
def product_fetch(product_id: int, product_name: Optional[str] = None,db: Session = Depends(get_db)):
    # Fix the filter condition - use proper SQLAlchemy syntax
    query = db.query(models.Product).filter(models.Product.id == product_id)
    if product_name:
        query = query.filter(func.lower(models.Product.name) == product_name.lower())
    
    product = query.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@app.put('/product/{product_id}/update')
def update_product(product_id:int, request: schemas.Product, db:Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'Product of id{product_id} not found')
    product.name = request.name
    product.description = request.description
    product.price = request.price
    product.is_available = request.is_available
    db.commit()
    db.refresh(product)
    return {"Message" : "Product sucessfully updated", "product":product}
