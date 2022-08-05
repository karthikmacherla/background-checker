from typing import Optional
from fastapi import APIRouter, Depends, UploadFile
from auth import get_current_user
from config import get_config
from logger import create_logger

import crud
import models


router = APIRouter(prefix="/user")
log = create_logger(__name__)
config = get_config()


@router.get("/", response_model=models.User)
def read_user(user=Depends(get_current_user)):
    return user
