from PyPDF2 import PdfReader
import io
from fastapi import HTTPException

def pdf_to_text(file, page_num=0):
    reader = PdfReader(file)
    text = ""
    if 0 <= page_num < len(reader.pages):
        page = reader.pages[page_num]
        text = page.extract_text() if page.extract_text() else ""
    else:
        raise HTTPException(status_code=400, detail="Invalid page number")
    return text

def extract_metadata(file):
    reader = PdfReader(file)
    metadata = reader.metadata
    return metadata