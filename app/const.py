import os
from fastapi import HTTPException, status


SECRET_KEY = os.getenv('SECRET_KEY')
USERS_DB = os.getenv('DATABASE_URL')
MEDIA_ASSETS = os.getenv('MEDIA_ASSETS')
DOC_PATH = os.getenv('DOC_PATH')
IMG_PATH = os.getenv('IMG_PATH')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
