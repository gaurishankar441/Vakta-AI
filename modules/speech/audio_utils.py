import io, wave

def pcm16_to_wav_bytes(pcm16: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """Wrap raw PCM16 LE into a WAV container."""
    bio = io.BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm16)
    return bio.getvalue()
