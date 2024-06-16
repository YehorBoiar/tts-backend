from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import nemo.collections.tts as nemo_tts
import torch
import soundfile as sf
from pydub import AudioSegment
from speech_synthesis import pdf_to_text, initialize_device, load_model, process_text_to_speech
import os

app = FastAPI()

# Update the origins list to include your Angular application's origin
origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://38.242.213.102:4200"
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

@app.post("/synthesize")
async def synthesize(file: UploadFile = File(...)):
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

