from dotenv import load_dotenv
from sqlalchemy import create_engine
from fastapi import HTTPException
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from backend.const import USERS_DB, MEDIA_ASSETS, DOC_PATH
from .models import Book
from io import BytesIO
from tts_utils.pdf_extraction import pdf_to_text  
import os

load_dotenv()
Base = declarative_base()

engine = create_engine(USERS_DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

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
    

def create_book(db: Session, path: str, metadata: dict) -> Book:
    new_book = Book(path=path, metadata_=metadata, paragraph_idx=0, page_idx=0)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

def get_all_books(db: Session, username: str) -> list[Book]:
    books = db.query(Book).filter(Book.path.like(f"%{username}%")).all()
    return books if books else []


def get_book(db: Session, username: str, book_id: int) -> Book:
    return db.query(Book).filter(Book.id == book_id, Book.path.like(f"%{username}%")).first()


def update_book_img_path(db: Session, book_path: str, img_path: str) -> None:
    book = db.query(Book).filter(Book.path == book_path).first()
    if book:
        book.metadata_['img_path'] = img_path
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Book not found")
