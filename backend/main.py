from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from .auth import authenticate_user, create_access_token, get_current_active_user, get_user_with_role
from .models import  Token, User, TextResponseModel, TextToSpeechRequest, ChunkTextResponse, ChunkTextRequest, TtsModelUpdateRequest
from .const import ACCESS_TOKEN_EXPIRE_MINUTES, CREDENTIALS_EXCEPTION, MEDIA_ASSETS, DOC_PATH, IMG_PATH, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_REGION
from tts_utils.pdf_extraction import pdf_to_text, extract_metadata, get_pages, first_page_jpeg, make_path, chunk_text, delete_file
from datetime import timedelta
from sqlalchemy import JSON
from sqlalchemy.orm import Session
from .register import register_user, UserCreate
from db.crud import get_all_users
from db.database import get_db
from db.books import create_book, save_file, get_all_books, get_book_image_path, delete_book
from db.tts_model import update_keys, get_model_by_path
from io import BytesIO
import logging
from botocore.exceptions import BotoCoreError, ClientError
import boto3

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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

polly_client = boto3.client(
    'polly',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/add_book", response_model=TextResponseModel)
def add_book_endpoint(
    db: Session = Depends(get_db), 
    pdf_file: UploadFile = File(...), 
    user: User = Depends(get_current_active_user)
):
    try:
        doc_path = make_path(MEDIA_ASSETS + DOC_PATH, user.username, pdf_file.filename)
        img_path = make_path(MEDIA_ASSETS + IMG_PATH, user.username, pdf_file.filename.replace('.pdf', '.jpeg'))

        if pdf_file.filename == '':
            raise HTTPException(status_code=400, detail="No selected file")

        file_content = BytesIO(pdf_file.file.read())

        if not save_file(file_content, doc_path):
            raise HTTPException(status_code=400, detail="File already exists")

        metadata = extract_metadata(file_content)
        metadata['img_path'] = img_path
        create_book(db, doc_path, metadata)
        
        image = first_page_jpeg(doc_path)
        
        if not save_file(image, img_path):
            raise HTTPException(status_code=500, detail="Failed to save image file")
        
        return {"text": "Book added successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/books", response_model=List[dict])
def get_books(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    books = get_all_books(db, user.username)
    return [{"metadata": book.metadata_, "path": book.path, "page": book.page_idx} for book in books]

@app.get("/get_book", response_model=TextResponseModel)
def get_book(path):
    text = pdf_to_text(path)
    return TextResponseModel(text=text)

@app.delete("/delete_book", response_model=TextResponseModel)
def delete(db: Session = Depends(get_db), path: str = None):
    logger.info(f"Received request to delete book with path: {path}")

    try:
        img_path = get_book_image_path(db, path)
        logger.info(f"Image path for book: {img_path}")

        if not delete_file(img_path):
            logger.error(f"Failed to delete image file: {img_path}")
            raise HTTPException(status_code=500, detail="Failed to delete image file")
        
        logger.info(f"Successfully deleted image file: {img_path}")

        if not delete_book(db, path):
            logger.error(f"Book not found in database: {path}")
            raise HTTPException(status_code=404, detail="Book not found")
        
        logger.info(f"Successfully deleted book record from database: {path}")

        if not delete_file(path):
            logger.error(f"Failed to delete book file: {path}")
            raise HTTPException(status_code=500, detail="Failed to delete file")
        
        logger.info(f"Successfully deleted book file: {path}")

        return TextResponseModel(text="Book deleted successfully")
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/get_image", response_class=FileResponse)
def get_image(db: Session = Depends(get_db), book_path: str = None):   
    image_path = get_book_image_path(db, book_path)
    return FileResponse(image_path, media_type='image/jpeg')
    

@app.get("/get_pages_num", response_model=TextResponseModel)
def get_pages_num(path):
    pages = get_pages(path)
    return TextResponseModel(text=str(len(pages)))

@app.get("/flip", response_model=TextResponseModel)
def flip_page(path, page_num):
    text = pdf_to_text(path, page_num)
    return TextResponseModel(text=text)

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

@app.post("/chunk_text", response_model=ChunkTextResponse)
def chunk_text_endpoint(request: ChunkTextRequest):
    chunks = chunk_text(request.text, request.chunk_size)
    return ChunkTextResponse(chunks=chunks)

@app.post("/synthesize_api")
def synthesize_speech(aws_access_key_id: str, aws_secret_access_key: str, region_name: str, request: TextToSpeechRequest):
    try:
        polly_client = boto3.client(
            'polly',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        response = polly_client.synthesize_speech(
            Text=request.text,
            OutputFormat='mp3',
            VoiceId=request.voice_id
        )

        if "AudioStream" in response:
            audio_stream = response["AudioStream"].read()
            return {"audio": audio_stream.hex()}
        else:
            raise HTTPException(status_code=500, detail="Error in synthesizing speech")

    except (BotoCoreError, ClientError) as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.post("/update_tts_model", response_model=TextResponseModel)
def update_tts_model(request: TtsModelUpdateRequest, db: Session = Depends(get_db)):
    logger.info(f"Received request to update TTS model: path={request.path}, model_name={request.model_name}, model_keys={request.model_keys}")
    try:
        result = update_keys(db, request.path, request.model_keys, request.model_name)
        if result:
            logger.info("TTS model added successfully.")
            return {"text": "TTS model added successfully"}
        else:
            logger.warning(f"No TTS model found for path: {request.path}, nothing updated.")
            raise HTTPException(status_code=404, detail="TTS model not found")
    except Exception as e:
        logger.error(f"Error updating TTS model: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/tts_model", response_model=dict)
def get_tts_model(db: Session = Depends(get_db), book_path: str = None):
    keys = get_model_by_path(db, book_path)
    return keys


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
