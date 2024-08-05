from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.models import User
from db.database import get_db
from db.crud import get_user_by_username, get_user_by_email, add_user
from jose import JWTError, jwt
from passlib.context import CryptContext
from schemas.user import TokenData, User
from const import SECRET_KEY, ALGORITHM, CREDENTIALS_EXCEPTION
from datetime import datetime, timedelta, timezone
from schemas.user import UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_data = TokenData(username=username)
    except JWTError:
        raise CREDENTIALS_EXCEPTION
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

async def get_user_with_role(role: str):
    def role_dependency(user: User = Depends(get_current_active_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return role_dependency

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def register_user(db: Session, user_create: UserCreate):
    # Check if the email already exists
    existing_user = get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if the username already exists
    existing_username = get_user_by_username(db, user_create.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash the password
    hashed_password = hash_password(user_create.password)
    
    # Add the new user to the database
    new_user = add_user(db, fullname=user_create.fullname, email=user_create.email, password=hashed_password, username=user_create.username, role=user_create.role)
    return new_user
