import nltk
import nemo.collections.tts as nemo_tts
import torch
import IPython.display as ipd
import soundfile as sf
from pydub import AudioSegment
from functools import partial
from typing import List
import PyPDF2
import io
import nltk

nltk.download('punkt')

def initialize_device() -> torch.device:
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_class, model_name: str, device: torch.device):
    model = model_class.from_pretrained(model_name=model_name)
    model.to(device)
    return model

def split_text(text: str) -> List[str]:
    return nltk.sent_tokenize(text)

def generate_spectrogram(tacotron2, sentence: str, device: torch.device) -> torch.Tensor:
    tokens = tacotron2.parse(sentence)
    with torch.no_grad():
        return tacotron2.generate_spectrogram(tokens=tokens.to(device))

def pdf_to_text(file_bytes):
    file_stream = io.BytesIO(file_bytes)
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text() if page.extract_text() else ""
    return text

def convert_to_audio(hifigan, spectrogram: torch.Tensor) -> AudioSegment:
    with torch.no_grad():
        audio = hifigan.convert_spectrogram_to_audio(spec=spectrogram)
    audio_numpy = audio.squeeze().cpu().numpy()
    temp_path = "temp.wav"
    sf.write(temp_path, audio_numpy, 22050)
    return AudioSegment.from_wav(temp_path)

def concatenate_audio(segments: List[AudioSegment]) -> AudioSegment:
    return sum(segments, AudioSegment.empty())

def process_text_to_speech(tacotron2, hifigan, device: torch.device, text: str) -> AudioSegment:
    sentences = split_text(text)
    spectrograms = map(partial(generate_spectrogram, tacotron2, device=device), sentences)
    audio_segments = map(partial(convert_to_audio, hifigan), spectrograms)
    return concatenate_audio(list(audio_segments))
