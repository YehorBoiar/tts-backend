from PyPDF2 import PdfReader
from typing import Dict, Any
from fastapi import HTTPException
from pdf2image import convert_from_path
from PIL import Image
import io
import os
from io import BytesIO


def make_path(media_path, username, filename):
    file_name = f"{username}_{filename}"
    return os.path.join(media_path, file_name)

def pdf_to_text(file, page_num=0):
    try:
        page_num = int(page_num)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid page number")
    reader = PdfReader(file)
    text = ""
    if 0 <= page_num < len(reader.pages):
        page = reader.pages[page_num]
        text = page.extract_text() if page.extract_text() else ""
    else:
        raise HTTPException(status_code=400, detail="Invalid page number")
    return text

def extract_metadata(file: str) -> Dict[str, Any]:
    reader = PdfReader(file)
    metadata = reader.metadata
    metadata_dict = {key: metadata[key] for key in metadata.keys()}
    return metadata_dict

def get_pages(file):
    return PdfReader(file).pages

def first_page_jpeg(file_path: str, dpi=300) -> BytesIO:
    try:
        # Convert only the first page of the PDF
        images = convert_from_path(file_path, first_page=1, last_page=1, dpi=dpi)
        if images:
            img = images[0]
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            return img_byte_arr
        else:
            raise HTTPException(status_code=500, detail="Failed to convert PDF to image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during PDF conversion: {e}")
