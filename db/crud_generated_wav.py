from sqlalchemy.orm import Session
from typing import List
from .models import GeneratedWav


def add_generated_wav(db: Session, username: str, pdf_file_name: str, wav_file_name: str, wav_file_path: str) -> GeneratedWav:
    new_wav = GeneratedWav(username=username, pdf_file_name=pdf_file_name, wav_file_name=wav_file_name, wav_file_path=wav_file_path)
    db.add(new_wav)
    db.commit()
    db.refresh(new_wav)
    return new_wav

def get_generated_wav_by_id(db: Session, wav_id: int) -> GeneratedWav:
    return db.query(GeneratedWav).filter(GeneratedWav.wav_id == wav_id).first()

def get_all_generated_wavs(db: Session) -> List[GeneratedWav]:
    return db.query(GeneratedWav).all()

def get_generated_wavs_by_username(db: Session, username: str) -> List[GeneratedWav]:
    return db.query(GeneratedWav).filter(GeneratedWav.username == username).all()

def update_generated_wav(db: Session, wav_id: int, pdf_file_name: str = None, wav_file_name: str = None, wav_file_path: str = None) -> GeneratedWav:
    wav_file = db.query(GeneratedWav).filter(GeneratedWav.wav_id == wav_id).first()
    if wav_file:
        if pdf_file_name:
            wav_file.pdf_file_name = pdf_file_name
        if wav_file_name:
            wav_file.wav_file_name = wav_file_name
        if wav_file_path:
            wav_file.wav_file_path = wav_file_path
        db.commit()
        db.refresh(wav_file)
        return wav_file
    return None

def delete_generated_wav(db: Session, wav_id: int) -> bool:
    wav_file = db.query(GeneratedWav).filter(GeneratedWav.wav_id == wav_id).first()
    if wav_file:
        db.delete(wav_file)
        db.commit()
        return True
    return False

def delete_all_generated_wavs(db: Session):
    db.query(GeneratedWav).delete()
    db.commit()
