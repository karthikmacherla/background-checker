from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from fastapi import Depends, APIRouter, status

from google.auth.transport import requests

from pydantic import BaseModel

from config import get_config
from auth import (
    authenticate_google_user,
    authenticate_user,
    create_access_token,
)

import models
import crud
import requests
from logger import create_logger

router = APIRouter(prefix="/login")

config = get_config()
log = create_logger(__name__)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/google")
def google_login_for_access_token(google_access_token: str):
    # attempt to decode
    try:
        # get info by making a request using the access_token they gave you
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {google_access_token}"},
        )
        
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid google access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        idinfo = resp.json()
        log.info(idinfo)

        userid = idinfo["email"]
        idinfo = models.GoogleInfo(
            name=idinfo["name"],
            picture=idinfo["picture"],
            given_name=idinfo["given_name"],
            family_name=idinfo["family_name"],
            sub=idinfo["sub"],
            email=idinfo["email"],
        )

        user = authenticate_google_user(userid, idinfo)
        access_token = create_access_token(data={"sub": user.email})
        return JSONResponse(
            {"access_token": access_token, "token_type": "bearer"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
    except ValueError as p:
        # Invalid token
        log.error(p)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication",
            headers={"WWW-Authenticate": "Bearer"},
        ) from p


@router.post("/username-json", response_model=Token)
async def login_for_access_token_json(form_data: models.UserCreate):
    user = authenticate_user(form_data.email, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email} )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/username", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup", response_model=Token)
async def signup_for_access_token(form_data: models.UserCreate):
    user = await crud.get_user_by_email(form_data.email)

    if user:
        log.debug(f"user: {user}")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User already exists",
        )
    log.info("User does not exist")
    user = await crud.create_user(form_data)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}