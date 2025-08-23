from typing import AsyncIterator, Optional
from openai import OpenAI
from app.core.config import settings

_client: Optional[OpenAI] = None
def _client_once():
    global _client
    if _client is None: _client = OpenAI()
    return _client

class OpenAITTS:
    def name(self): return "openai"
    async def complete(self, text: str) -> AsyncIterator[bytes]:
        client = _client_once()
        model = getattr(settings, "TTS_MODEL", "gpt-4o-mini-tts")
        voice = getattr(settings, "TTS_VOICE", "alloy")
        try:
            with client.audio.speech.with_streaming_response.create(model=model, voice=voice, input=text) as resp:
                for chunk in resp.iter_bytes():
                    yield chunk
        except Exception:
            # graceful no-op if provider not reachable
            if False:
                yield b""
            return

class EdgeTTS:
    async def complete(self, text: str) -> AsyncIterator[bytes]:
        if False:
            yield b""
        return
