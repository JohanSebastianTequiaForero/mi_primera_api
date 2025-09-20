from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import User, Product, Favorite
from .schemas import UserRegister, UserLogin, Token, UserResponse, ProductCreate, ProductResponse, FavoriteResponse
from .auth import get_password_hash, verify_password, create_access_token, get_current_user, require_admin
from fastapi import FastAPI
from .database import engine, Base
from .models import User, Product, Favorite # Make sure to import all your models

app = FastAPI()

# This is the key part that creates the tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# 🔴 OBLIGATORIOS - Core de Autenticación
@app.post("/register", response_model=UserResponse)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=Token)
def login_for_access_token(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/protected")
def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, you are authenticated."}

@app.get("/admin-only")
def admin_only_endpoint(current_user: User = Depends(require_admin)):
    return {"message": "Welcome, Admin. This is a restricted area."}

# Implement the optional endpoints (products and favorites) here using the provided schemas and dependencies.
# The logic for these endpoints would be similar to the examples in the project description.