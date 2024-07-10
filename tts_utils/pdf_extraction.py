import PyPDF2
import io
from fastapi import HTTPException

def pdf_to_text(file_bytes, page_num=0):
    file_stream = io.BytesIO(file_bytes)
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    if 0 <= page_num < len(reader.pages):
        page = reader.pages[page_num]
        text = page.extract_text() if page.extract_text() else ""
    else:
        raise HTTPException(status_code=400, detail="Invalid page number")
    return text
