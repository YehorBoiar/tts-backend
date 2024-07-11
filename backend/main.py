from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import nemo.collections.tts as nemo_tts
from typing import List
from .auth import authenticate_user, create_access_token, get_current_active_user, get_user_with_role
from .models import  Token, User, TextResponseModel
from .const import ACCESS_TOKEN_EXPIRE_MINUTES, CREDENTIALS_EXCEPTION, MEDIA_ASSETS, DOC_PATH
from tts_utils.tts_utils import initialize_device, load_model, process_text_to_speech
from tts_utils.pdf_extraction import pdf_to_text, extract_metadata
import os
from datetime import timedelta
from sqlalchemy.orm import Session
from .register import register_user, UserCreate
from db.crud import get_all_users
from db.database import get_db
from db.books import create_book, save_file, get_all_books, get_book
from io import BytesIO


app = FastAPI()

# Update the origins list to include your Angular application's origin
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://38.242.213.102:3000",
    "http://students.codevery.win/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = initialize_device()
tacotron2 = load_model(nemo_tts.models.Tacotron2Model, "tts_en_tacotron2", device)
hifigan = load_model(nemo_tts.models.HifiGanModel, "tts_en_hifigan", device)

@app.post("/add_book", response_model=TextResponseModel)
def add_book_endpoint(db: Session = Depends(get_db), pdf_file: UploadFile = File(...), user: User = Depends(get_current_active_user)):
    if pdf_file.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")
    
    file_content = BytesIO(pdf_file.file.read())
    if not save_file(file_content, user.username, pdf_file.filename):
        raise HTTPException(status_code=400, detail="File already exists")
    
    metadata = extract_metadata(file_content)
    author = metadata.author
    title = metadata.title
    
    book = create_book(db, pdf_file.filename, user.username, author, title, metadata)
    
    return JSONResponse(content={"message": "Book added successfully", "book_title": book.title}) 

@app.get("/books", response_model=List[dict])
def get_books(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    books = get_all_books(db, user.username)
    return [{"title": book.title, "author": book.author, "metadata": book.metadata_} for book in books]

@app.get("/get_book", response_model=TextResponseModel)
def get_book(book_name: str, user: User = Depends(get_current_active_user)):
    path = MEDIA_ASSETS + DOC_PATH + user.username + "_" + book_name
    return pdf_to_text(path)

@app.post("/text", response_model=TextResponseModel)
def get_text(pdf_file: UploadFile = File(...)):
    if not pdf_file:
        raise HTTPException(status_code=400, detail="No file part")
    if pdf_file.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")
    text = pdf_to_text(pdf_file.file.read())
    return {"text": text}

@app.post("/register", response_model=UserCreate)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    new_user = register_user(db, user_create)
    return new_user

@app.get("/profile/me", response_model=User)
async def read_own_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/admin/users", response_model=List[User])
async def read_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_user_with_role("admin"))):
    users = get_all_users(db)
    return users

@app.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise CREDENTIALS_EXCEPTION
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/synthesize")
async def synthesize(file: UploadFile = File(...)):
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")

    pdf_content = await file.read()
    text = pdf_to_text(pdf_content)
    full_audio = process_text_to_speech(tacotron2, hifigan, device, text)
    
    output_path = "output.wav"
    full_audio.export(output_path, format="wav")
    
    return FileResponse(output_path, media_type='audio/wav', filename=os.path.basename(output_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=80)
