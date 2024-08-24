from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Optional

from app.models import User as UserModel
from app.models import User as  UserSchema
from app.schemas import  UserCreate, UserUpdate


SECRET_KEY ="mysecretkey"
EXPIRE_MINUTES = 60 * 24
ALGORITHUM = "HS256"


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
bcrypt_context = CryptContext(schemes=["bcrypt"])

# Check existing user
async def existing_user(db:Session, username:str,email:str):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user:
        return db_user
    db_user = db.query(UserModel).filter(UserModel.email == email).first()
    if db_user:
        return db_user
    return None

# jwt = {encoded data, secret_key, algorithum}
# create token
async def create_access_token(id:int, username:str):
    encode = {"sub":username, "id":id}
    expires:datetime = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    encode.update({"exp":expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHUM)


# # get current user from token
async def get_current_user(db: Session, token:str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHUM])
        username:str = payload.get("sub")
        id:int = payload.get("id") 
        expires:datetime = payload.get("exp")
        if datetime.fromtimestamp(expires) < datetime.utcnow():
            return None
        if username is None or id is None:
            return None
        db_user = db.query(UserModel).filter(UserModel.id == id).first()
        return db_user
    except JWTError:
        return None


#create user
async def create_user(db:Session, user:UserCreate):
    db_user = UserModel(
    username = user.username,
    email = user.email,
    hashed_password = bcrypt_context.hash(user.password),)
    db.add(db_user)
    db.commit()
    return db_user




    
#authenticate_service
async def authenticate(db: Session, username: str, password: str):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if not db_user:
        return None
    if not bcrypt_context.verify(password, db_user.hashed_password):
        return None
    return db_user
    

async def update_user(db:Session,db_user:UserModel, user_update:UserUpdate):
    db_user.email = user_update.email or db_user.email
    # save
    db.commit()
    db.refresh(db_user)
