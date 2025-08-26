# utils/voice.py
"""
Optional: Convert an audio file to text. This uses Whisper library as a placeholder.
If you prefer cloud speech to text, replace this with calls to Google Speech API.
"""
import whisper
model = None

def load_whisper_model(name="small"):
    global model
    if model is None:
        model = whisper.load_model(name)
    return model

def transcribe_audio_file(path):
    m = load_whisper_model()
    res = m.transcribe(path)
    # return transcription text
    return res.get("text", "")
