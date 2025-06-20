from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from backend.database import engine, SessionLocal
from backend.database import Base
import backend.models as models
import backend.schemas as schemas
import backend.hashing as hashing
from backend.schemas import Login
from typing import Optional
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from backend.hashing import Hash
from backend.auth_token import create_access_token
from backend.oauth2 import get_current_user
from fastapi.staticfiles import StaticFiles
from typing import List
import shutil
import os

app = FastAPI()

# Create static directory and mount static files
static_dir = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
if not os.path.exists(os.path.join(static_dir, "images")):
    os.makedirs(os.path.join(static_dir, "images"))

app.mount("/static", StaticFiles(directory=static_dir), name="static")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Ecommerce API is running! 🚀"}

@app.post('/create_user', tags = ["user"])
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
    
@app.post('/user/login', tags = ['user'])
def login_user(request: Login, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail = 'Invalid credentials'
            )
    if not Hash.verify(request.password, user.password):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND, detail = "invalid password"
        )
    token = create_access_token(data={"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.get('/profile', tags =['user'])
def get_profile(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

'''getting all the registered user as the api'''
@app.get('/registered_user', tags = ['user'])
def show_users(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.put('/user/{user_id}/update', tags = ['user'])
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
    
@app.delete('/user/delete/{user_id}', tags = ['user'])
def delete_user(user_id:int, db:Session = Depends(get_db))->None:
    result = db.query(models.User).filter(models.User.id == user_id).delete(synchronize_session=False)
    db.commit()
    if result == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User with {user_id} not found")
    return {"message" : "User deleted succesfully"}

if not os.path.exists("images"):
    os.makedirs("images")

@app.post("/add_product", response_model=schemas.Product, tags =['products'])
async def add_product(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    is_available: bool = Form(False),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check for existing product (case-insensitive)
    existing = db.query(models.Product).filter(func.lower(models.Product.name) == name.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")

    # Save uploaded image to 'static/images' folder
    image_dir = os.path.join(os.getcwd(), "static", "images")
    os.makedirs(image_dir, exist_ok=True)
    image_location = os.path.join(image_dir, image.filename)
    
    try:
        with open(image_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        print(f"Image saved successfully to: {image_location}")
    except Exception as e:
        print(f"Error saving image: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    # Save product with correct image URL path
    image_url = f"/static/images/{image.filename}"
    new_product = models.Product(
        name=name,
        description=description,
        price=price,
        is_available=is_available,
        image_url=image_url  # served from FastAPI static files
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    print(f"Product created with image_url: {image_url}")
    return new_product


@app.get("/all_products", response_model=List[schemas.Product], tags=['products'])
def all_products(skip: int = 0, limit: int = 10, name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if name:
        query = query.filter(models.Product.name.ilike(f'{name}%'))
    return query.offset(skip).limit(limit).all()

@app.delete('/product/{product_id}/delete', tags=['products'])
def delete_product(product_id:int, db:Session = Depends(get_db)):
    result = db.query(models.Product).filter(models.Product.id == product_id).delete(synchronize_session=False)
    db.commit()
    if result == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Product with id {product_id} not found")
    return "Product deletion succesful"

@app.get('/product/{product_id}', tags = ['products'])
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

@app.put('/product/{product_id}/update', tags = ['products'])
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

@app.put('/product/{product_id}/update_image', tags = ['products'])
def update_product_image(product_id: int, image: UploadFile = File(...), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Product of id {product_id} not found')
    
    # Save uploaded image to 'static/images' folder
    image_dir = os.path.join(os.getcwd(), "static", "images")
    os.makedirs(image_dir, exist_ok=True)
    image_location = os.path.join(image_dir, image.filename)
    with open(image_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Update product image URL
    product.image_url = f"/static/images/{image.filename}"
    db.commit()
    db.refresh(product)
    return {"Message": "Product image successfully updated", "product": product}

@app.get('/fix_product_images', tags = ['products'])
def fix_product_images(db: Session = Depends(get_db)):
    """Fix existing product image URLs to use the correct static path"""
    products = db.query(models.Product).all()
    fixed_count = 0
    
    for product in products:
        if product.image_url and product.image_url.startswith('/images/'):
            # Update old /images/ paths to /static/images/
            product.image_url = product.image_url.replace('/images/', '/static/images/')
            fixed_count += 1
    
    if fixed_count > 0:
        db.commit()
        return {"message": f"Fixed {fixed_count} product image URLs"}
    else:
        return {"message": "No product image URLs needed fixing"}


@app.post('/product/cart', response_model=schemas.CartItemResponse, tags = ['products'])
def add_to_cart(item: schemas.CartItemCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Add to cart
    cart_item = models.CartItem(product_id=item.product_id, quantity=item.quantity)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item
@app.get("/cart", response_model=List[schemas.CartItemWithProduct], tags = ['products'])
def get_cart(db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).options(joinedload(models.CartItem.product)).all()
    return cart_items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)