from typing import Optional
from openai import OpenAI
from app.core.config import settings
from .audio_utils import pcm16_to_wav_bytes

_client: Optional[OpenAI] = None
def _client_once():
    global _client
    if _client is None: _client = OpenAI()
    return _client

class OpenAIASR:
    def name(self): return "openai"
    async def complete(self, pcm16: bytes, sample_rate: int = 16000) -> str:
        wav = pcm16_to_wav_bytes(pcm16, sample_rate)
        model = getattr(settings, "ASR_MODEL", "gpt-4o-mini-transcribe")
        client = _client_once()
        try:
            resp = client.audio.transcriptions.create(model=model, file=("speech.wav", wav))
            return (resp.text or "").strip()
        except Exception:
            return ""
        
class WhisperXASR:
    """Placeholder fallback implementation."""
    def name(self): return "whisperx"
    async def complete(self, pcm16: bytes, sample_rate: int = 16000) -> str:
        return ""
