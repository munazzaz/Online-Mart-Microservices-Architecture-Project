from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, Token, TokenData, UserUpdate
from app.deps import get_kafka_producer
import json
from app.settings import KAFKA_USER_TOPIC
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio

app = FastAPI(
    title="User Service API",
    version="0.0.1",
    description = "The User Service API is a foundational component for managing user registration, authentication, and authorization, ensuring secure access to your platform. ",
    servers=[
        {
            "url": "http://127.0.0.1:8008/",
            "description": "Local Development Server"
        }
        ]
)


# Security setup
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/signup", response_model=dict)
async def create_user(user: UserCreate, db: Session = Depends(get_db), producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.username})
    user_data = {
        "action": "create",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    }
    await producer.send_and_wait(KAFKA_USER_TOPIC, json.dumps(user_data).encode('utf-8'))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": db_user.username,
        "detail": "User created successfully"
    }

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    user_data = {
        "action": "login",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }
    await producer.send_and_wait(KAFKA_USER_TOPIC, json.dumps(user_data).encode('utf-8'))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/update", response_model=UserOut)
async def update_user(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    if user_update.email:
        db_user_with_email = db.query(User).filter(User.email == user_update.email).first()
        if db_user_with_email and db_user_with_email.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email
    if user_update.password:
        hashed_password = get_password_hash(user_update.password)
        current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    user_data = {
        "action": "update",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        }
    }
    await producer.send_and_wait(KAFKA_USER_TOPIC, json.dumps(user_data).encode('utf-8'))
    return current_user

@app.delete("/delete", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    user_data = {
        "action": "delete",
        "user": {
            "id": current_user.id
        }
    }
    await producer.send_and_wait(KAFKA_USER_TOPIC, json.dumps(user_data).encode('utf-8'))
    return {"detail": "User deleted successfully"}




@app.get("/users/{user_id}", response_model=UserOut)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
