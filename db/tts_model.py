from .models import TtsModel, Book
from sqlalchemy.orm import Session
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_model_by_path(db: Session, path) -> dict:
    tts_model = db.query(TtsModel).filter(TtsModel.path == path).first()
    if tts_model:
        return {"name": tts_model.model_name, "keys": tts_model.model_keys}
    return None

def update_keys(db: Session, path: str, keys: dict, model_name: str="standard"):
    logger.info(f"Attempting to update keys for path: {path} with model_name: {model_name} and keys: {keys}")
    tts_model = db.query(TtsModel).filter(TtsModel.path == path).first()
    if tts_model:
        logger.info(f"Found TTS model for path: {path}. Updating model_name and keys.")
        tts_model.model_name = model_name
        tts_model.model_keys = keys
        db.commit()
        logger.info(f"Model updated successfully for path: {path}")
        return tts_model
    logger.warning(f"No TTS model found for path: {path}")
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