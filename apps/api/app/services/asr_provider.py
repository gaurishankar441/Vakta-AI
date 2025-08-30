import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe raw audio bytes using OpenAI Whisper API.
    """
    try:
        resp = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",  # fast Whisper
            file=("input.wav", audio_bytes)
        )
        return resp.text
    except Exception as e:
        return f"[ASR error: {e}]"
