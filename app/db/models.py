from sqlalchemy import Column, Integer, String, ForeignKey, JSON
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

class TtsModel(Base):
    __tablename__ = 'tts_model'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    model_keys = Column(JSON)
    path = Column(String(512), ForeignKey('book.path'))

    books = relationship("Book", back_populates="tts_model")

class Book(Base):
    __tablename__ = 'book'

    path = Column(String(512), primary_key=True)
    metadata_ = Column("metadata", JSON)
    page_idx = Column(Integer, default=0)

    tts_model = relationship("TtsModel", back_populates="books")