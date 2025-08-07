# app_with_auth.py - Complete Avatar-Enhanced Vakta AI with LARGE AVATAR DISPLAY
import streamlit as st
import requests
import json
import speech_recognition as sr
import pyttsx3
import io
import tempfile
import os
import random
import threading
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Avatar Configuration
AVATAR_PERSONALITIES = {
    "priya": {
        "name": "Priya Madam",
        "description": "Friendly Hindi-English teacher",
        "style": "encouraging",
        "color": "#FF6B6B",
        "emoji_base": "👩‍🏫",
        "expressions": {
            "neutral": "👩‍🏫",
            "happy": "😊",
            "excited": "🤩", 
            "thinking": "🤔",
            "celebrating": "🎉",
            "encouraging": "💪"
        }
    },
    "alex": {
        "name": "Alex Sir", 
        "description": "Professional English tutor",
        "style": "structured",
        "color": "#4ECDC4",
        "emoji_base": "👨‍🏫",
        "expressions": {
            "neutral": "👨‍🏫",
            "happy": "😄",
            "excited": "⭐",
            "thinking": "💭", 
            "celebrating": "🏆",
            "encouraging": "👍"
        }
    },
    "maya": {
        "name": "Maya Didi",
        "description": "Fun learning buddy",
        "style": "playful",
        "color": "#45B7D1", 
        "emoji_base": "👱‍♀️",
        "expressions": {
            "neutral": "👱‍♀️",
            "happy": "😁",
            "excited": "🎊",
            "thinking": "🧠",
            "celebrating": "🎈", 
            "encouraging": "🌟"
        }
    }
}

# Enhanced CSS for better avatar display
AVATAR_CSS = """
<style>
.avatar-main {
    text-align: center;
    margin: 2rem 0;
    animation: gentle-bounce 3s ease-in-out infinite;
}

.avatar-large {
    font-size: 6rem !important;
    line-height: 1.2;
    margin: 1rem 0;
    filter: drop-shadow(4px 4px 8px rgba(0,0,0,0.15));
}

.avatar-medium {
    font-size: 3rem !important;
    line-height: 1.2;
    margin: 0.5rem 0;
    filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
}

.avatar-small {
    font-size: 2rem !important;
    line-height: 1.2;
    margin: 0.25rem 0;
}

@keyframes gentle-bounce {
    0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-8px);
    }
    60% {
        transform: translateY(-4px);
    }
}

.avatar-speaking {
    animation: speaking-pulse 1.5s ease-in-out infinite;
}

@keyframes speaking-pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
}

.response-container {
    animation: fade-in 0.6s ease-in;
}

@keyframes fade-in {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

.avatar-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(248,249,250,0.9));
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
}

.main-header {
    text-align: center;
    color: #1E88E5;
    margin-bottom: 2rem;
}

.stButton > button {
    width: 100%;
    border-radius: 20px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
"""

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'voice_mode' not in st.session_state:
    st.session_state.voice_mode = False
if 'selected_avatar' not in st.session_state:
    st.session_state.selected_avatar = "priya"
if 'avatar_expression' not in st.session_state:
    st.session_state.avatar_expression = "neutral"

def make_api_request(endpoint, method="GET", data=None, auth_required=False):
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth_required and st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                return error_data
            except:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}

def send_chat_message(message):
    """Send chat message to AI"""
    data = {"message": message}
    result = make_api_request("/chat", method="POST", data=data, auth_required=True)
    
    if result.get("success"):
        return {
            "response": result["data"]["response"],
            "fluency_score": result["data"]["fluency_score"],
            "session_id": result["data"]["session_id"],
            "processing_time_ms": result["data"]["processing_time_ms"],
            "conversation_id": result["data"].get("conversation_id")
        }
    else:
        if "errors" in result:
            error_msg = result["errors"][0] if result["errors"] else "Chat failed"
        else:
            error_msg = result.get("message", "Chat failed")
        return {"error": error_msg}

def get_user_profile():
    """Get user profile information"""
    result = make_api_request("/users/me", method="GET", auth_required=True)
    
    if result.get("success"):
        return result["data"]["user"]
    else:
        return None

def get_avatar_expression(fluency_score, is_speaking=False):
    """Determine avatar expression based on context"""
    if is_speaking:
        return "thinking"
    elif fluency_score >= 80:
        return "celebrating"
    elif fluency_score >= 60:
        return "excited" 
    elif fluency_score >= 40:
        return "happy"
    elif fluency_score >= 20:
        return "encouraging"
    else:
        return "neutral"

def display_avatar(expression="neutral", size="large", show_name=True, animated=True):
    """Enhanced avatar display with better visibility"""
    avatar_config = AVATAR_PERSONALITIES[st.session_state.selected_avatar]
    
    # Get the right emoji based on expression
    if expression in avatar_config["expressions"]:
        avatar_emoji = avatar_config["expressions"][expression]
    else:
        avatar_emoji = avatar_config["emoji_base"]
    
    # Animation class
    animation_class = "avatar-speaking" if expression == "thinking" else ""
    
    # Create enhanced avatar HTML
    avatar_html = f"""
    <div class="avatar-main {animation_class}">
        <div class="avatar-card" style="background: linear-gradient(135deg, {avatar_config['color']}15, {avatar_config['color']}05);">
            <div class="avatar-{size}">
                {avatar_emoji}
            </div>
            {f'''
            <h3 style="margin: 0.5rem 0; color: {avatar_config["color"]}; font-weight: bold;">
                {avatar_config["name"]}
            </h3>
            <p style="margin: 0; font-size: 1rem; color: #666; font-style: italic;">
                {avatar_config["description"]}
            </p>
            ''' if show_name else ''}
        </div>
    </div>
    """
    
    st.markdown(avatar_html, unsafe_allow_html=True)

def avatar_response_with_expression(ai_response, fluency_score):
    """Display AI response with appropriate avatar expression"""
    expression = get_avatar_expression(fluency_score)
    st.session_state.avatar_expression = expression
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        display_avatar(expression, size="medium", show_name=False)
    
    with col2:
        avatar_config = AVATAR_PERSONALITIES[st.session_state.selected_avatar]
        
        response_html = f"""
        <div class="response-container" style="
            background: linear-gradient(135deg, {avatar_config['color']}22, {avatar_config['color']}11);
            border-left: 4px solid {avatar_config['color']};
            padding: 1.5rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        ">
            <strong style="color: {avatar_config['color']}; font-size: 1.1rem;">
                🤖 {avatar_config['name']}:
            </strong><br><br>
            <div style="font-size: 1rem; line-height: 1.6;">
                {ai_response.replace(chr(10), '<br>')}
            </div>
        </div>
        """
        
        st.markdown(response_html, unsafe_allow_html=True)

def show_avatar_selection():
    """Enhanced avatar selection interface"""
    st.subheader("🎭 Choose Your AI Tutor")
    
    cols = st.columns(len(AVATAR_PERSONALITIES))
    
    for i, (avatar_id, config) in enumerate(AVATAR_PERSONALITIES.items()):
        with cols[i]:
            is_selected = st.session_state.selected_avatar == avatar_id
            border_style = f"3px solid {config['color']}" if is_selected else "2px solid #ddd"
            bg_style = f"linear-gradient(135deg, {config['color']}25, {config['color']}10)" if is_selected else "#f8f9fa"
            
            st.markdown(f"""
            <div style="
                text-align: center; 
                padding: 1.5rem; 
                border-radius: 15px; 
                background: {bg_style}; 
                border: {border_style};
                transition: all 0.3s ease;
                cursor: pointer;
            ">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{config['emoji_base']}</div>
                <strong style="font-size: 1.1rem;">{config['name']}</strong><br>
                <small style="color: #666;">{config['description']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Select {config['name']}", key=f"select_{avatar_id}", use_container_width=True):
                st.session_state.selected_avatar = avatar_id
                st.session_state.avatar_expression = "happy"
                st.success(f"✨ {config['name']} is now your tutor!")
                st.rerun()

def avatar_welcome_message():
    """Enhanced welcome message with avatar"""
    if st.session_state.user_info:
        user_name = st.session_state.user_info.get('full_name', 'Student')
        avatar_config = AVATAR_PERSONALITIES[st.session_state.selected_avatar]
        
        welcome_messages = {
            "priya": f"नमस्ते {user_name}! I'm Priya, your friendly language teacher. Let's practice English together! 🌟",
            "alex": f"Hello {user_name}! I'm Alex, your professional English tutor. Ready for structured learning? 📚",
            "maya": f"Hey {user_name}! I'm Maya, your fun learning buddy! Let's make language learning exciting! 🎉"
        }
        
        message = welcome_messages.get(st.session_state.selected_avatar, f"Hello {user_name}!")
        
        # Enhanced welcome message display
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {avatar_config['color']}20, {avatar_config['color']}08);
            border: 2px solid {avatar_config['color']}40;
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">
                {avatar_config['expressions']['happy']}
            </div>
            <strong style="color: {avatar_config['color']}; font-size: 1.2rem;">
                💬 {message}
            </strong>
        </div>
        """, unsafe_allow_html=True)

def display_conversation_with_avatar(conversation):
    """Display conversation with avatar expressions"""
    fluency_score = conversation['fluency_score']
    
    # User message
    st.markdown(f"**👤 You:** {conversation['user_message']}")
    
    # Avatar response
    avatar_response_with_expression(conversation['ai_response'], fluency_score)
    
    # Score display with avatar reaction
    score_reactions = [
        (80, "🎉 Excellent! I'm so proud!"),
        (60, "😊 Great progress!"),
        (40, "👍 Good effort!"), 
        (20, "💪 Keep practicing!"),
        (0, "🌱 Every start is beautiful!")
    ]
    
    reaction = next((msg for score, msg in score_reactions if fluency_score >= score), "Keep going! 🌟")
    st.caption(f"Avatar reaction: {reaction}")

def record_voice():
    """Record voice input"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... Please speak clearly!")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=10, phrase_time_limit=30)
        
        st.info("🔄 Processing your speech...")
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("❌ Could not understand audio. Please try again.")
        return None
    except sr.RequestError as e:
        st.error(f"❌ Speech recognition error: {e}")
        return None
    except sr.WaitTimeoutError:
        st.error("❌ No speech detected. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Voice recording error: {e}")
        return None

def play_text_to_speech(text):
    """Convert text to speech - Streamlit compatible"""
    try:
        import pyttsx3
        import threading
        import time
        
        def speak_text():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.8)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                st.error(f"❌ TTS Engine Error: {str(e)}")
        
        # Run TTS in separate thread
        tts_thread = threading.Thread(target=speak_text)
        tts_thread.daemon = True
        tts_thread.start()
        
        st.success("🔊 Playing audio... (Check your speakers)")
        time.sleep(0.5)
        
    except ImportError:
        st.error("❌ TTS library not available")
    except Exception as e:
        st.error(f"❌ TTS Error: {str(e)}")
        st.info("🔊 **Read this aloud for practice:**")
        st.markdown(f"*\"{text}\"*")

def show_login_page():
    """Display login/register interface"""
    st.title("🗣️ Vakta AI – Practice Your Language Skills")
    st.markdown("**Your AI-powered language learning companion with avatar tutors**")
    
    # Show sample avatars with better display
    st.subheader("🎭 Meet Your AI Tutors")
    cols = st.columns(3)
    sample_avatars = list(AVATAR_PERSONALITIES.items())
    for i, (avatar_id, config) in enumerate(sample_avatars):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {config['color']}22, {config['color']}11); border-radius: 15px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">{config['emoji_base']}</div>
                <strong style="color: {config['color']};">{config['name']}</strong><br>
                <small>{config['description']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    # Login Tab
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                if email and password:
                    with st.spinner("Logging in..."):
                        login_data = {"email": email, "password": password}
                        result = make_api_request("/login", method="POST", data=login_data)
                        
                        if result.get("success"):
                            token = result["data"]["access_token"]
                            user_info = result["data"]["user"]
                            
                            st.session_state.logged_in = True
                            st.session_state.auth_token = token
                            st.session_state.user_info = user_info
                            st.success(f"Welcome back, {user_info['full_name']}! 🎉")
                            st.rerun()
                        else:
                            if "errors" in result:
                                error_msg = result["errors"][0] if result["errors"] else "Login failed"
                            else:
                                error_msg = result.get("message", "Login failed")
                            st.error(f"❌ {error_msg}")
                else:
                    st.error("⚠️ Please fill all fields")
    
    # Register Tab
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            new_email = st.text_input("Email", key="reg_email", placeholder="your.email@example.com")
            new_full_name = st.text_input("Full Name", key="reg_full_name", placeholder="John Doe")
            new_password = st.text_input("Password", type="password", key="reg_password", 
                                       help="Minimum 8 characters")
            
            col1, col2 = st.columns(2)
            with col1:
                primary_language = st.selectbox("Native Language", 
                                              ["Hindi", "English", "Spanish", "French", "Tamil", "Telugu"])
            with col2:
                target_language = st.selectbox("Learning Language", 
                                             ["English", "Hindi", "Spanish", "French"])
            
            register_button = st.form_submit_button("🎯 Create Account", use_container_width=True)
            
            if register_button:
                if all([new_email, new_full_name, new_password]):
                    if len(new_password) < 8:
                        st.error("⚠️ Password must be at least 8 characters long")
                    else:
                        with st.spinner("Creating account..."):
                            lang_codes = {
                                "Hindi": "hi", "English": "en", "Spanish": "es", 
                                "French": "fr", "Tamil": "ta", "Telugu": "te"
                            }
                            
                            register_data = {
                                "full_name": new_full_name,
                                "email": new_email,
                                "password": new_password,
                                "primary_language": lang_codes.get(primary_language, "hi"),
                                "target_language": lang_codes.get(target_language, "en")
                            }
                            
                            result = make_api_request("/register", method="POST", data=register_data)
                            
                            if result.get("success"):
                                st.success("🎉 Account created successfully! Please login now.")
                                st.balloons()
                            else:
                                if "errors" in result:
                                    error_msg = result["errors"][0] if result["errors"] else "Registration failed"
                                else:
                                    error_msg = result.get("message", "Registration failed")
                                st.error(f"❌ {error_msg}")
                else:
                    st.error("⚠️ Please fill all fields")

def show_chat_page():
    """Display main chat interface with enhanced avatar"""
    
    # Add custom CSS
    st.markdown(AVATAR_CSS, unsafe_allow_html=True)
    
    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1>🗣️ Vakta AI</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # LARGE MAIN AVATAR DISPLAY
    display_avatar(st.session_state.avatar_expression, size="large", show_name=True)
    
    # User info and controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        user_name = st.session_state.user_info.get('full_name', 'User')
        st.markdown(f"**Welcome, {user_name}!** 👋")
    with col2:
        if st.button("🎭 Change Tutor"):
            with st.expander("Choose Your AI Tutor", expanded=True):
                show_avatar_selection()
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.auth_token = None
            st.session_state.user_info = None
            st.session_state.conversation_history = []
            st.rerun()
    
    # Welcome message from avatar
    avatar_welcome_message()
    st.divider()
    
    # Voice mode toggle
    col1, col2 = st.columns([1, 3])
    with col1:
        voice_mode = st.toggle("🎤 Voice Mode", value=st.session_state.voice_mode)
        st.session_state.voice_mode = voice_mode
    
    if voice_mode:
        st.info("🎙️ **Voice Mode Active** - Your avatar is listening!")
    
    # Chat input
    if voice_mode:
        col1, col2 = st.columns([3, 1])
        with col1:
            user_input = st.text_input("💬 Type your message or use voice:", 
                                     placeholder="You can type here or click 'Speak'...")
        with col2:
            st.write("")
            if st.button("🎤 Speak", use_container_width=True):
                st.session_state.avatar_expression = "thinking"
                st.rerun()  # Update avatar immediately
                voice_text = record_voice()
                if voice_text:
                    user_input = voice_text
                    st.success(f"🗣️ You said: '{voice_text}'")
                    st.session_state.avatar_expression = "happy"
    else:
        user_input = st.text_input("💬 Type your message:", 
                                 placeholder="Start practicing! Your avatar is ready to help...")
    
    # Send message
    if st.button("📤 Send Message", use_container_width=True, disabled=not user_input):
        if user_input.strip():
            st.session_state.avatar_expression = "thinking"
            st.rerun()  # Show thinking avatar immediately
            
            with st.spinner("🤖 Your tutor is thinking..."):
                result = send_chat_message(user_input.strip())
                
                if "error" not in result:
                    fluency_score = result["fluency_score"]
                    new_expression = get_avatar_expression(fluency_score)
                    st.session_state.avatar_expression = new_expression
                    
                    conversation = {
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "user_message": user_input.strip(),
                        "ai_response": result["response"],
                        "fluency_score": result["fluency_score"],
                        "processing_time": result.get("processing_time_ms", 0),
                        "avatar_expression": new_expression
                    }
                    st.session_state.conversation_history.append(conversation)
                    
                    # Success message with avatar celebration
                    if fluency_score >= 80:
                        st.balloons()
                        st.success(f"🎉 Excellent! Your tutor is celebrating! Score: **{fluency_score}/100**")
                    elif fluency_score >= 60:
                        st.success(f"⭐ Great job! Your tutor is excited! Score: **{fluency_score}/100**")
                    else:
                        st.success(f"👍 Good effort! Your tutor is encouraging you! Score: **{fluency_score}/100**")
                    
                    st.rerun()  # Update avatar with new expression
                else:
                    st.session_state.avatar_expression = "encouraging"
                    st.error(f"❌ {result['error']}")
    
    st.divider()
    
    # Conversation history with avatar
    if st.session_state.conversation_history:
        st.subheader("💬 Conversation History")
        
        for i, conv in enumerate(reversed(st.session_state.conversation_history[-10:])):
            with st.expander(f"💬 {conv['timestamp']} - Score: {conv['fluency_score']}/100", expanded=(i==0)):
                
                display_conversation_with_avatar(conv)
                
                # Metrics
                score = conv['fluency_score']
                if score >= 80:
                    level = "Advanced"
                    avatar_comment = "I'm so proud of your progress! 🎉"
                elif score >= 50:
                    level = "Intermediate"
                    avatar_comment = "You're improving nicely! 😊"
                else:
                    level = "Beginner"
                    avatar_comment = "Keep practicing, you'll get there! 💪"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fluency Score", f"{score}/100")
                with col2:
                    st.metric("Level", level)
                with col3:
                    st.metric("Response Time", f"{conv['processing_time']}ms")
                
                st.caption(f"🎭 {AVATAR_PERSONALITIES[st.session_state.selected_avatar]['name']}: {avatar_comment}")
                
                # TTS with avatar
                if st.button(f"🔊 Listen to {AVATAR_PERSONALITIES[st.session_state.selected_avatar]['name']}", key=f"tts_{i}"):
                    st.session_state.avatar_expression = "thinking" 
                    play_text_to_speech(conv['ai_response'])
    
    else:
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        with col1:
            display_avatar("happy", size="medium", show_name=False)
        with col2:
            st.info("👋 **Your AI tutor is ready!** Start your conversation now!")
            st.markdown("""
            **💡 Tips for better scores:**
            - Use complete sentences with proper punctuation
            - Include connecting words like 'and', 'but', 'because'
            - Express your opinions and ask questions
            - Use varied vocabulary and sentence structures
            """)
    
    # Enhanced sidebar
    with st.sidebar:
        st.subheader("🎭 Your AI Tutor")
        
        avatar_config = AVATAR_PERSONALITIES[st.session_state.selected_avatar]
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {avatar_config['color']}25, {avatar_config['color']}10); border-radius: 15px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{avatar_config['emoji_base']}</div>
            <strong style="color: {avatar_config['color']};">{avatar_config['name']}</strong><br>
            <small>{avatar_config['description']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📊 Your Progress")
        
        profile = get_user_profile()
        if profile:
            st.metric("Total Conversations", profile.get('total_conversations', 0))
            avg_score = profile.get('average_fluency_score', 0)
            st.metric("Average Score", f"{avg_score:.1f}/100")
            
            progress = min(avg_score / 100, 1.0)
            st.progress(progress, text=f"Overall Progress: {avg_score:.1f}%")
            
            # Avatar encouragement
            if avg_score >= 80:
                st.success("🎉 Your tutor says: Excellent progress!")
            elif avg_score >= 60:
                st.info("😊 Your tutor says: You're doing great!")
            elif avg_score >= 40:
                st.info("👍 Your tutor says: Keep up the good work!")
            else:
                st.info("💪 Your tutor says: Practice makes perfect!")
        
        st.divider()
        
        st.subheader("⚙️ Settings")
        if st.button("🗑️ Clear History"):
            st.session_state.conversation_history = []
            st.session_state.avatar_expression = "happy"
            st.success("History cleared! Avatar is ready for fresh start! ✨")
            st.rerun()
        
        st.subheader("🔌 System Status")
        health_result = make_api_request("/health")
        if health_result.get("success"):
            st.success("🟢 Backend Online")
        else:
            st.error("🔴 Backend Offline")

def main():
    """Main application"""
    st.set_page_config(
        page_title="Vakta AI - Avatar Language Learning",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown(AVATAR_CSS, unsafe_allow_html=True)
    
    # Check authentication
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_chat_page()

if __name__ == "__main__":
    main()
