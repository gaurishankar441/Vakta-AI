# modules/speech_to_text.py

import os
import whisper

# Load Whisper model only once
model = whisper.load_model("base")

def transcribe_audio(audio_path):
    """
    Transcribes speech from the given audio file using OpenAI's Whisper.
    Automatically detects language and returns both text and language code.
    
    :param audio_path: Path to the .wav audio file
    :return: Tuple (transcribed text, language code)
    """
    if not os.path.exists(audio_path):
        return "", "en"

    try:
        # 🔍 Run whisper transcription
        result = model.transcribe(audio_path)
        
        text = result.get("text", "").strip()
        lang = result.get("language", "en")

        # 🛡️ Fallback if no text detected
        if not text:
            return "", lang

        return text, lang

    except Exception as e:
        print(f"❌ Whisper Transcription Error: {e}")
        return "", "en"
