from dotenv import load_dotenv
from sqlalchemy import create_engine
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

def save_file(file_obj: BytesIO, username: str, filename: str):
    """
    Save the file to the media assets.

    Parameters:
    file_obj (BytesIO): The file object to be saved.
    """
    destination = MEDIA_ASSETS + DOC_PATH + username + "_" + filename
    try:
        with open(destination, 'wb') as f:
            f.write(file_obj.getbuffer())
        print(f"File saved successfully to {destination}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")    

def add_book(db: Session, filename: str, username: str, author: str, title: str, metadata: dict) -> Book:
    destination = MEDIA_ASSETS + DOC_PATH + username + "_" + filename
    add_file_to_documents(destination)
    new_book = Book(path=destination, author=author, title=title, metadata=metadata)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

