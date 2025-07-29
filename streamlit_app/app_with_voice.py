# streamlit_app/app_with_voice.py

import streamlit as st
import requests
import pyttsx3
import speech_recognition as sr
import io

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)

# API Config
API_URL = "http://localhost:8000/chat"
TOKEN = None  # You can integrate token auth here if needed

# Record voice
def record_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Please speak")
        audio = r.listen(source, phrase_time_limit=5)

    try:
        text = r.recognize_google(audio)
        st.success(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        st.warning("⚠️ Could not understand your voice.")
        return ""
    except sr.RequestError:
        st.error("❌ Speech recognition service failed.")
        return ""

# Speak response
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# App UI
st.set_page_config(page_title="Vakta Voice", layout="centered")
st.title("🗣️ Vakta AI - Voice Mode")

voice_mode = st.toggle("Enable Voice Mode")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = ""

if voice_mode:
    if st.button("🎙️ Speak"):
        user_input = record_voice()
else:
    user_input = st.text_input("Type your message")

if user_input:
    st.session_state.chat_history.append(("You", user_input))

    with st.spinner("Vakta AI is thinking..."):
        response = requests.post(
            API_URL,
            json={"message": user_input},
            headers={"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        )

        if response.status_code == 200:
            data = response.json()
            bot_reply = data.get("response")
            fluency = data.get("fluency_score")

            st.session_state.chat_history.append(("Vakta AI", bot_reply))
            st.success(f"Fluency Score: {fluency}/100")

            if voice_mode:
                speak_text(bot_reply)
        else:
            st.error("Failed to get AI response")

# Display history
for sender, msg in st.session_state.chat_history[::-1]:
    st.markdown(f"**{sender}:** {msg}")
