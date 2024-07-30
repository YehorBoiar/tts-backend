from pydantic import BaseModel, EmailStr, Field, validator
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db.crud import add_user, get_user_by_email, get_user_by_username
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic model for user registration
class UserCreate(BaseModel):
    fullname: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    username: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="user")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# Function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_email(user_email: str):
    """Function that sends a verification email to the user."""
    
    sender_email = "youremail@example.com"
    sender_password = "yourpassword"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    subject = "Verify your email address"
    body = f"Please click the link to verify your email address: http://example.com/verify?email={user_email}"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, user_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Registration function
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
    
    verify_email(user_create.email)
    # Hash the password
    hashed_password = hash_password(user_create.password)
    
    # Add the new user to the database
    new_user = add_user(db, fullname=user_create.fullname, email=user_create.email, password=hashed_password, username=user_create.username, role=user_create.role)
    return new_user