from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from jose import JWTError, jwt

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext

import crud
import models
from logger import create_logger

# from schemas import *
# from utils import *
from config import get_config

config = get_config()
log = create_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/username")

""" 
password hashing + verification

"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_hash_from_str(s: str):
    return pwd_context.hash(s)



""" 
Auth functions for dependency injection

"""

async def authenticate_user(username: str, password: str) -> models.User:
    user = await crud.get_user_by_email(username)
    log.info(user)
    if user and verify_password(password, user.hashed_password):
        return user


def authenticate_google_user(
    user_id: str, idinfo: models.GoogleInfo
) -> models.User:
    gen_pwd = get_hash_from_str(user_id)
    user = crud.get_user_by_email(user_id)

    if not user:
        # create the user with idinfo
        userObj = UserCreate(
            email=idinfo.email,
            name=idinfo.name,
            profile_pic_url=idinfo.picture,
            password=gen_pwd,
        )
        user = crud.create_user(userObj)
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret, algorithm=config.hash_algo)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=[config.hash_algo])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = models.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await crud.get_user_by_email(token_data.username)
    log.debug(f"user {user.email},{user.name}")
    if user is None:
        raise credentials_exception
    return user
