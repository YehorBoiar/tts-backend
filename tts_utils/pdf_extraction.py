from PyPDF2 import PdfReader
from typing import Dict, Any
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


def extract_metadata(file: str) -> Dict[str, Any]:
    reader = PdfReader(file)
    metadata = reader.metadata
    metadata_dict = {key: metadata[key] for key in metadata.keys()}
    return metadata_dict
