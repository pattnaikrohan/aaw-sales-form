import json
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from jose import JWTError, jwt
import bcrypt
from models.schemas import UserCreate, UserLogin, Token, UserResponse

router = APIRouter()

# Setup hashing and JWT
SECRET_KEY = "aaw-sales-app-super-secret-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

USERS_DB_FILE = os.path.join(os.path.dirname(__file__), "..", "users.json")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def load_users():
    if not os.path.exists(USERS_DB_FILE):
        return {}
    try:
        with open(USERS_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    users = load_users()
    
    if user.email in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    hashed_password = get_password_hash(user.password)
    users[user.email] = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }
    
    save_users(users)
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "name": user.name}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    users = load_users()
    
    db_user = users.get(user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    access_token = create_access_token(data={"sub": db_user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "name": db_user["name"]}

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid auth token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid auth token")
        
    users = load_users()
    user = users.get(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
        
    return {"name": user["name"], "email": user["email"]}
