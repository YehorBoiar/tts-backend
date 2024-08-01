from .models import TtsModel, Book
from sqlalchemy.orm import Session


def get_model_keys_by_path(db: Session, path) -> dict:
    tts_model = db.query(TtsModel).filter(TtsModel.path == path).first()
    if tts_model:
        return tts_model.model_keys
    return None

def update_keys(db: Session, path: str, keys: dict, model_name: str="standard"):
    tts_model = db.query(TtsModel).filter(TtsModel.path == path).first()
    if tts_model:
        tts_model.model_name = model_name
        tts_model.model_keys = keys
        db.commit()
        return tts_model
    return None

def get_all_tts_models(db: Session):
    return db.query(TtsModel).all()

def delete_tts_model(db: Session, model_id):
    tts_model = db.query(TtsModel).filter(TtsModel.id == model_id).first()
    if tts_model:
        db.delete(tts_model)
        db.commit()
        return True
    return False