from fastapi import HTTPException
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from const import USERS_DB
from .models import User, Book, TtsModel
import logging
from io import BytesIO
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def create_book(db: Session, path: str, metadata: dict) -> Book:
    logger.info(f'Creating a new book with path: {path} and metadata: {metadata}')
    new_book = Book(path=path, metadata_=metadata, page_idx=0)
    
    # Create the associated TtsModel with standard values
    new_tts_model = TtsModel(
        model_name="standard",
        model_keys={},
        path=path
    )

    try:
        db.add(new_book)
        db.add(new_tts_model)
        db.commit()
        db.refresh(new_book)
        logger.info(f'Book created with path: {new_book.path}')
        return new_book
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f'Failed to create book with path: {path}. Error: {e}')
        return None

def save_file(file_obj: BytesIO, file_path: str) -> bool:
    """
    Save the file to the media assets.

    Parameters:
    file_obj (BytesIO): The file object to be saved.
    """

    if os.path.exists(file_path):
        print(f"File already exists. Skipping save.")
        return False

    try:
        with open(f"{file_path}", 'wb') as f:
            f.write(file_obj.getbuffer())
        print(f"File saved successfully to {file_path}")
        return True
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
        return False
    
def get_all_books(db: Session, username: str) -> list[Book]:
    books = db.query(Book).filter(Book.path.like(f"%{username}%")).all()
    return books if books else []

def get_book_image_path(db: Session, book_path: str) -> str:
    book = db.query(Book).filter(Book.path == book_path).first()
    if book:
        return book.metadata_['img_path']
    else:
        raise HTTPException(status_code=404, detail="Book not found")
    
def delete_book(db: Session, path: str) -> bool:
    book = db.query(Book).filter(Book.path == path).first()
    if book:
        db.delete(book)
        db.commit()
        return True
    else:
        return False

def update_keys(db: Session, path: str, keys: dict, model_name: str="standard"):
    logger.info(f"Attempting to update keys for path: {path} with model_name: {model_name} and keys: {keys}")
    tts_model = db.query(TtsModel).filter(TtsModel.path == path).first()
    if tts_model:
        logger.info(f"Found TTS model for path: {path}. Updating model_name and keys.")
        tts_model.model_name = model_name
        tts_model.model_keys = keys
        db.commit()
        logger.info(f"Model updated successfully for path: {path}")
        return tts_model
    logger.warning(f"No TTS model found for path: {path}")
    return None

def get_model_by_path(db: Session, path) -> dict:
    tts_model = db.query(TtsModel).filter(TtsModel.path == path).first()
    if tts_model:
        return {"name": tts_model.model_name, "keys": tts_model.model_keys}
    return None