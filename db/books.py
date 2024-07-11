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

def save_file(file_obj: BytesIO, username: str, filename: str) -> bool:
    """
    Save the file to the media assets.

    Parameters:
    file_obj (BytesIO): The file object to be saved.
    """
    destination = os.path.join(MEDIA_ASSETS, DOC_PATH)
    file_name = f"{username}_{filename}"
    file_path = os.path.join(destination, file_name)

    if os.path.exists(file_path):
        print(f"File {file_name} already exists. Skipping save.")
        return False
    
    file_obj.name = username + "_" + filename

    try:
        with open(f"{destination + file_obj.name}", 'wb') as f:
            f.write(file_obj.getbuffer())
        print(f"File saved successfully to {destination}")
        return True
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
        return False
    

def create_book(db: Session, filename: str, username: str, author: str, title: str, metadata: dict) -> Book:
    destination = MEDIA_ASSETS + DOC_PATH + username + "_" + filename
    new_book = Book(path=destination, author=author, title=title, metadata=metadata)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book
