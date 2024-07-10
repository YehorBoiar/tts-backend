from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from backend.const import USERS_DB
from .models import Book
from io import BytesIO
from tts_utils.pdf_extraction import pdf_to_text  


load_dotenv()
Base = declarative_base()

engine = create_engine(USERS_DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def add_book(db: Session, pdf_file: BytesIO, author: str, title: str, metadata: dict) -> Book:
    content = pdf_to_text(pdf_file)
    new_book = Book(content=content, author=author, title=title, metadata=metadata)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

