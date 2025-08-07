import streamlit as st
import time
import random

st.set_page_config(page_title="🎭 Vakta AI", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.card { background: white; padding: 2rem; border-radius: 15px; margin: 2rem auto; max-width: 800px; }
.chat-msg { padding: 1rem; margin: 0.5rem 0; border-radius: 10px; }
.user-msg { background: #4ECDC4; color: white; }
.ai-msg { background: #667eea; color: white; }
.tutor-card { background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; text-align: center; border: 2px solid #ddd; }
.voice-section { background: #f0f8ff; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state:
    st.session_state.auth = False
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_tutor" not in st.session_state:
    st.session_state.current_tutor = "priya"
if "page" not in st.session_state:
    st.session_state.page = "login"
if "recorded_text" not in st.session_state:
    st.session_state.recorded_text = ""

TUTORS = {
    'priya': {'name': 'Priya', 'language': 'Hindi/English', 'emoji': '🇮🇳'},
    'alex': {'name': 'Alex', 'language': 'English', 'emoji': '🇺🇸'},
    'maya': {'name': 'Maya', 'language': 'Spanish/English', 'emoji': '🇪🇸'}
}

def get_response(user_input, tutor_key):
    user_lower = user_input.lower()
    
    if "hi" in user_lower or "hello" in user_lower:
        responses = {
            'priya': f"Namaste! Main Priya hun. Aapne kaha '{user_input}' - welcome!",
            'alex': f"Hello! I'm Alex. Your greeting '{user_input}' is perfect!",
            'maya': f"Hola! Soy Maya. Your '{user_input}' has great energy!"
        }
    elif "learn" in user_lower:
        responses = {
            'priya': f"Wah! Learning enthusiasm dekh kar khushi hui!",
            'alex': f"Excellent! Your dedication to learning is admirable!",
            'maya': f"Fantastico! Learning with passion is the best way!"
        }
    else:
        responses = {
            'priya': f"Accha! Aapne kaha '{user_input}' - interesting point!",
            'alex': f"Good input! '{user_input}' shows thoughtful communication!",
            'maya': f"Que bueno! Your message '{user_input}' is wonderful!"
        }
    
    return responses[tutor_key], random.randint(70, 95)

def get_voice_input():
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("🎤 Listening... Speak now!")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        text = r.recognize_google(audio)
        return True, text
    except ImportError:
        return False, "Install: pip install speechrecognition pyaudio"
    except Exception as e:
        return False, f"Error: {str(e)}"

def speak_response(text):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
        return True
    except:
        return False

if not st.session_state.auth:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🎭 Vakta AI")
    st.write("Language Learning with Voice Support")
    if st.button("🚀 Start"):
        st.session_state.auth = True
        st.session_state.page = "tutor_selection"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "tutor_selection":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🎭 Choose Your Tutor")
    
    for tutor_key, tutor in TUTORS.items():
        st.markdown(f"""
        <div class="tutor-card">
            <h4>{tutor['emoji']} {tutor['name']}</h4>
            <p>{tutor['language']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Select {tutor['name']}", key=tutor_key):
            st.session_state.current_tutor = tutor_key
            st.session_state.page = "main"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    current_tutor = TUTORS[st.session_state.current_tutor]
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title(f"🎭 Learning with {current_tutor['name']}")
    
    if st.button("🔄 Change Tutor"):
        st.session_state.page = "tutor_selection"
        st.rerun()
    
    # Voice section
    st.markdown('<div class="voice-section">', unsafe_allow_html=True)
    st.subheader("🎤 Voice Input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎤 Start Recording"):
            with st.spinner("Recording..."):
                success, result = get_voice_input()
                if success:
                    st.session_state.recorded_text = result
                    st.success(f"Recorded: {result}")
                else:
                    st.error(result)
    
    with col2:
        if st.session_state.recorded_text and st.button("📤 Send Voice"):
            user_input = st.session_state.recorded_text
            ai_response, score = get_response(user_input, st.session_state.current_tutor)
            
            st.session_state.conversations.append({
                "user": user_input, "ai": ai_response, "score": score, "tutor": current_tutor['name']
            })
            
            # Speak the response
            speak_response(ai_response)
            
            st.session_state.recorded_text = ""
            st.rerun()
    
    if st.session_state.recorded_text:
        st.info(f"🎤 Recorded: {st.session_state.recorded_text}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Text input (existing)
    with st.form("chat", clear_on_submit=True):
        user_input = st.text_input("Type Message:")
        if st.form_submit_button("📤 Send") and user_input:
            ai_response, score = get_response(user_input, st.session_state.current_tutor)
            st.session_state.conversations.append({
                "user": user_input, "ai": ai_response, "score": score, "tutor": current_tutor['name']
            })
            st.rerun()
    
    # Show conversations
    if st.session_state.conversations:
        st.subheader("💬 Conversation")
        for conv in st.session_state.conversations[-5:]:
            st.markdown(f'<div class="chat-msg user-msg">You: {conv["user"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-msg ai-msg">{conv["tutor"]}: {conv["ai"]} (Score: {conv["score"]})</div>', unsafe_allow_html=True)
    
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.session_state.page = "login"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
