# modules/text_to_speech.py

from gtts import gTTS
import os
import tempfile
import pygame

# 🗣️ Speak text in the detected language
def speak_text(text, lang="en"):
    try:
        # 🌐 gTTS supports limited language codes; map if needed
        lang_map = {
            "en": "en",
            "hi": "hi",
            "fr": "fr",
            "es": "es",
            "de": "de"
        }
        lang_code = lang_map.get(lang, "en")

        # 🔊 Create temp audio file
        tts = gTTS(text=text, lang=lang_code, slow=False)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
            tts.save(fp.name)

            # 🕹️ Play audio using pygame
            pygame.mixer.init()
            pygame.mixer.music.load(fp.name)
            pygame.mixer.music.play()

            # ⏱️ Wait until audio finishes playing
            while pygame.mixer.music.get_busy():
                continue

    except Exception as e:
        print(f"❌ TTS Error: {e}")
