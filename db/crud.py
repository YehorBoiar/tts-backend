import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from ..backend.const import USERS_DB
from .models import User

load_dotenv()

Base = declarative_base()

engine = create_engine(USERS_DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def add_user(db: Session, fullname: str, email: str, password: str, username: str, role: str = "user") -> User:
    new_user = User(fullname=fullname, email=email, password=password, username=username, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, username: str, fullname: str = None, email: str = None, password: str = None) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        if fullname:
            user.fullname = fullname
        if email:
            user.email = email
        if password:
            user.password = password
        db.commit()
        db.refresh(user)
        return user
    return None

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session):
    return db.query(User).all()

def delete_user(db: Session, username: str) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def delete_all_users(db: Session):
    db.query(User).delete()
    db.commit()
