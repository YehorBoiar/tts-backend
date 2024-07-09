from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text, JSON, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    fullname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    username = Column(String(255), primary_key=True, index=True)
    role = Column(String(50), nullable=False, default="user")

    generated_wavs = relationship("GeneratedWav", order_by="GeneratedWav.wav_id", back_populates="user")
    user_progress = relationship("UserProgress", order_by="UserProgress.book_id", back_populates="user")


class GeneratedWav(Base):
    __tablename__ = 'generated_wavs'
    
    wav_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), ForeignKey('users.username'), nullable=False)
    pdf_file_name = Column(String(255), nullable=False)
    wav_file_name = Column(String(255), nullable=False)
    wav_file_path = Column(String(255), nullable=False)
    generation_date = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="generated_wavs")


class Book(Base):
    __tablename__ = 'book'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author = Column(String(255))
    title = Column(String(255))
    metadata = Column(JSON)

    user_progress = relationship("UserProgress", order_by="UserProgress.user_id", back_populates="book")


class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True, nullable=False)
    user_id = Column(String(255), ForeignKey('users.username'), primary_key=True, nullable=False)
    paragraph_idx = Column(Integer, default=0, nullable=False)
    page_idx = Column(Integer, default=0, nullable=False)

    book = relationship("Book", back_populates="user_progress")
    user = relationship("User", back_populates="user_progress")
