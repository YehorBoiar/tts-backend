from pydantic import BaseModel
from typing import List


class TextToSpeechRequest(BaseModel):
    text: str
    voice_id: str = "Joanna"
    
class TextResponseModel(BaseModel):
    text: str


class ChunkTextRequest(BaseModel):
    text: str
    chunk_size: int = 3000

class ChunkTextResponse(BaseModel):
    chunks: List[str]
