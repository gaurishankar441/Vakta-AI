# modules/audio_input.py

import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

def record_audio(duration=5, filename="data/temp_audio.wav", samplerate=44100):
    print("🎙️ Recording started... Speak now!")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("✅ Recording complete.")

    # Make sure 'data/' folder exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    write(filename, samplerate, recording)
    print(f"📁 Audio saved to: {filename}")
    return filename
