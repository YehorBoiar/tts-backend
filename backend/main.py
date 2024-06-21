from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import nemo.collections.tts as nemo_tts
import torch
import soundfile as sf
from pydub import AudioSegment
from typing import List
from auth import authenticate_user, create_access_token, get_current_active_user, Token, User, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
from tts_utils import pdf_to_text, initialize_device, load_model, process_text_to_speech
import os
from datetime import timedelta

app = FastAPI()

# Update the origins list to include your Angular application's origin
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://38.242.213.102:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = initialize_device()
tacotron2 = load_model(nemo_tts.models.Tacotron2Model, "tts_en_tacotron2", device)
hifigan = load_model(nemo_tts.models.HifiGanModel, "tts_en_hifigan", device)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/synthesize")
async def synthesize(file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)):
    if not file:
        return {"error": "No file part"}, 400
    if file.filename == '':
        return {"error": "No selected file"}, 400

    pdf_content = await file.read()
    text = pdf_to_text(pdf_content)
    full_audio = process_text_to_speech(tacotron2, hifigan, device, text)
    output_path = "output.wav"
    full_audio.export(output_path, format="wav")

    return FileResponse(output_path, media_type='audio/wav', filename=os.path.basename(output_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
