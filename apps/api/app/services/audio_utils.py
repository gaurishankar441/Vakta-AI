import io, wave
from typing import Union

def pcm16_to_wav_bytes(pcm16: Union[bytes, bytearray], sample_rate: int = 16000, channels: int = 1) -> bytes:
    """Raw little-endian 16-bit PCM ko in-memory WAV bytes me convert karta hai."""
    if not isinstance(pcm16, (bytes, bytearray)):
        raise TypeError("pcm16 must be bytes/bytearray")
    # odd length safety (2 bytes per sample)
    if len(pcm16) % 2:
        pcm16 = pcm16[:-1]
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16)
    return buf.getvalue()
