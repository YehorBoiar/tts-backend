import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    ID = Column(Integer, primary_key=True)
    fullname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_user(fullname, email, password):
    existing_user = session.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"User with email {email} already exists.")
        return None
    new_user = User(fullname=fullname, email=email, password=password)
    session.add(new_user)
    session.commit()
    return new_user

def update_user(user_id, fullname=None, email=None, password=None):
    user = session.query(User).filter(User.ID == user_id).first()
    if user:
        if fullname:
            user.fullname = fullname
        if email:
            user.email = email
        if password:
            user.password = password
        session.commit()
        return user
    return None

def get_user_by_id(user_id):
    return session.query(User).filter(User.ID == user_id).first()

def get_all_users():
    return session.query(User).all()

def delete_user(user_id):
    user = session.query(User).filter(User.ID == user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return True
    return False

def delete_all_users():
    session.query(User).delete()
    session.commit()

