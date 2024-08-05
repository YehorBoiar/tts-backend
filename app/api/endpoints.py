from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from io import BytesIO
from const import MEDIA_ASSETS, DOC_PATH, IMG_PATH, CREDENTIALS_EXCEPTION, ACCESS_TOKEN_EXPIRE_MINUTES
from db.database import get_db
from db.crud import create_book, save_file, get_all_books, get_book_image_path, delete_book
from schemas.user import User
from schemas.book import TextResponseModel
from core.security import get_current_active_user, authenticate_user, create_access_token
from utils.pdf_utils import extract_metadata, first_page_jpeg, make_path, pdf_to_text, delete_file, get_pages
from schemas.user import Token
from datetime import timedelta
from typing import List
import logging 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/get_image", response_class=FileResponse)
def get_image(db: Session = Depends(get_db), book_path: str = None):   
    image_path = get_book_image_path(db, book_path)
    return FileResponse(image_path, media_type='image/jpeg')
    

@router.get("/get_pages_num", response_model=TextResponseModel)
def get_pages_num(path):
    pages = get_pages(path)
    return TextResponseModel(text=str(len(pages)))

@router.delete("/delete_book", response_model=TextResponseModel)
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
    
@router.get("/books", response_model=List[dict])
def get_books(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    books = get_all_books(db, user.username)
    return [{"metadata": book.metadata_, "path": book.path, "page": book.page_idx} for book in books]

@router.get("/get_book", response_model=TextResponseModel)
def get_book(path):
    text = pdf_to_text(path)
    return TextResponseModel(text=text)

@router.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise CREDENTIALS_EXCEPTION
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/add_book", response_model=TextResponseModel)
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


