import streamlit as st
import time
import random
from datetime import datetime

# Page config
st.set_page_config(
    page_title="🎭 Vakta AI - Language Learning",
    page_icon="🎭",
    layout="wide"
)

# Safe CSS - No content hiding issues
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .content-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem auto;
        max-width: 800px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .feature-box {
        background: rgba(78, 205, 196, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4ECDC4;
    }
    
    .tutor-box {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        border: 2px solid #ddd;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    .user-message {
        background: #4ECDC4;
        color: white;
        margin-left: 20%;
    }
    
    .ai-message {
        background: #667eea;
        color: white;
        margin-right: 20%;
    }
    
    .avatar-display {
        background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_tutor' not in st.session_state:
    st.session_state.current_tutor = 'priya'

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

if 'total_conversations' not in st.session_state:
    st.session_state.total_conversations = 0

# Tutor data
TUTORS = {
    'priya': {
        'name': 'Priya',
        'language': 'Hindi/English',
        'personality': 'Friendly Hindi teacher who mixes Hindi and English',
        'greeting': 'Namaste! Main Priya hun. Aaj kya sikhenge?',
        'color': '#FF6B6B'
    },
    'alex': {
        'name': 'Alex',
        'language': 'English',
        'personality': 'Professional English teacher focused on grammar',
        'greeting': 'Hello! I\'m Alex. Ready to improve your English skills?',
        'color': '#4ECDC4'
    },
    'maya': {
        'name': 'Maya',
        'language': 'Spanish/English',
        'personality': 'Creative Spanish teacher with lots of energy',
        'greeting': '¡Hola! Soy Maya. Let\'s explore languages together!',
        'color': '#A8E6CF'
    }
}

# Enhanced AI Response function with better variety
def get_ai_response(user_input, tutor_key):
    user_input = user_input.strip().lower()
    
    # Context-aware responses based on user input
    if any(word in user_input for word in ['hello', 'hi', 'namaste', 'hola']):
        greetings = {
            'priya': [
                "Namaste! Bahut khushi hui aapko dekhkar! Aaj conversation practice karenge?",
                "Arrey wah! Hello! Main Priya hun, aapka Hindi-English tutor. Kaise hain aap?",
                "Sat Sri Akal! Aaj kya naya sikhenge together?"
            ],
            'alex': [
                "Hello there! Great to see you're ready to practice English today!",
                "Hi! I'm excited to help you improve your English communication skills.",
                "Good to meet you! Let's work on building your confidence in English."
            ],
            'maya': [
                "¡Hola! ¡Qué bueno verte! Ready for some amazing language practice?",
                "Hello! I'm Maya, and I'm thrilled to help you explore languages!",
                "¡Fantástico! Let's make language learning fun and engaging today!"
            ]
        }
    elif any(word in user_input for word in ['learn', 'study', 'practice']):
        learning_responses = {
            'priya': [
                f"Bilkul! '{user_input}' - learning ke liye motivation bahut important hai!",
                f"Wah! Aap practice karna chahte hain? Main help karungi step by step!",
                f"Perfect! Sikhne ka josh dekh kar khushi hui. Let's start!"
            ],
            'alex': [
                f"Excellent mindset! Your interest in '{user_input}' shows dedication to learning.",
                f"That's the spirit! Consistent practice is key to language mastery.",
                f"Great approach! Let's structure your learning journey effectively."
            ],
            'maya': [
                f"¡Me encanta! Your enthusiasm for '{user_input}' is absolutely wonderful!",
                f"Amazing! Learning with passion makes all the difference!",
                f"¡Perfecto! Let's make your learning journey exciting and memorable!"
            ]
        }
    elif any(word in user_input for word in ['good', 'fine', 'okay', 'great']):
        positive_responses = {
            'priya': [
                f"Bahut accha! Aapka positive attitude dekh kar maja aa gaya!",
                f"Shabash! '{user_input}' - ye confidence language learning mein helpful hai!",
                f"Excellent! Aapka energy contagious hai, keep it up!"
            ],
            'alex': [
                f"Wonderful! Your positive response '{user_input}' shows great attitude.",
                f"That's exactly the mindset needed for effective language learning!",
                f"Perfect! Maintaining positivity accelerates your progress significantly."
            ],
            'maya': [
                f"¡Increíble! Your positive energy with '{user_input}' lights up our session!",
                f"Fantastic! I can feel your enthusiasm radiating through our conversation!",
                f"¡Maravilloso! This positive vibe will supercharge your learning!"
            ]
        }
    else:
        # General conversation responses
        general_responses = {
            'priya': [
                f"Interesting! Aapne kaha '{user_input}' - iske baare mein aur batayiye!",
                f"Accha! '{user_input}' ke context mein main aur examples de sakti hun.",
                f"Samjha! Aapka point '{user_input}' bilkul valid hai. Let's explore more!",
                f"Bahut badhiya! '{user_input}' - aise sentences grammar improve karte hain!"
            ],
            'alex': [
                f"I see! Your statement '{user_input}' opens up interesting discussion points.",
                f"That's insightful! '{user_input}' demonstrates good language comprehension.",
                f"Excellent observation! Your input '{user_input}' shows analytical thinking.",
                f"Very good! '{user_input}' - let's build on this foundation."
            ],
            'maya': [
                f"¡Qué interesante! Your thought '{user_input}' sparks creative possibilities!",
                f"Amazing perspective! '{user_input}' shows your unique way of thinking!",
                f"¡Brillante! Your expression '{user_input}' has such wonderful energy!",
                f"Fantastic! '{user_input}' - I love how you're engaging with language!"
            ]
        }
    
    # Select appropriate response set
    if any(word in user_input for word in ['hello', 'hi', 'namaste', 'hola']):
        response_set = greetings
    elif any(word in user_input for word in ['learn', 'study', 'practice']):
        response_set = learning_responses
    elif any(word in user_input for word in ['good', 'fine', 'okay', 'great']):
        response_set = positive_responses
    else:
        response_set = general_responses
    
    response = random.choice(response_set[tutor_key])
    
    # Dynamic fluency scoring based on input complexity
    word_count = len(user_input.split())
    char_count = len(user_input)
    
    base_score = min(95, max(60, char_count * 1.5 + word_count * 3))
    fluency_score = int(base_score + random.randint(-5, 10))
    
    return response, fluency_score

# Login Page
def show_login():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.title("🎭 Vakta AI")
    st.subheader("Advanced Language Learning Platform")
    st.write("Master languages with AI-powered tutors and immersive conversations")
    
    # Features
    st.markdown("""
    <div class="feature-box">
        <h4>🎯 AI-Powered Tutors</h4>
        <p>Choose from 3 specialized tutors: Priya (Hindi), Alex (English), Maya (Spanish)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>💬 Interactive Conversations</h4>
        <p>Real-time chat with personalized feedback and fluency scoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>📊 Progress Tracking</h4>
        <p>Monitor your learning journey with detailed analytics and achievements</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    if st.button("🚀 Start Learning Journey", type="primary", use_container_width=True):
        st.session_state.authenticated = True
        st.session_state.current_page = 'tutor_selection'
        st.success("🎉 Welcome to Vakta AI!")
        time.sleep(1)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tutor Selection Page
def show_tutor_selection():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    st.title("🎭 Choose Your AI Tutor")
    st.write("Select the tutor that matches your learning goals:")
    
    cols = st.columns(3)
    
    for i, (tutor_key, tutor) in enumerate(TUTORS.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="tutor-box" style="border-color: {tutor['color']};">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
                <h4 style="color: {tutor['color']};">{tutor['name']}</h4>
                <p><strong>Language:</strong> {tutor['language']}</p>
                <p style="font-size: 0.9rem;">{tutor['personality']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Select {tutor['name']}", key=f"select_{tutor_key}", use_container_width=True):
                st.session_state.current_tutor = tutor_key
                st.session_state.current_page = 'main'
                
                # Add greeting to conversation
                st.session_state.conversation_history.append({
                    'speaker': 'ai',
                    'message': tutor['greeting'],
                    'timestamp': datetime.now().strftime("%H:%M"),
                    'fluency_score': None
                })
                
                st.success(f"✅ {tutor['name']} selected as your tutor!")
                time.sleep(1)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main Chat Interface
def show_main_chat():
    current_tutor = TUTORS[st.session_state.current_tutor]
    
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"🎭 Learning with {current_tutor['name']}")
    with col2:
        if st.button("🔄 Change Tutor"):
            st.session_state.current_page = 'tutor_selection'
            st.rerun()
    
    # Main layout
    chat_col, avatar_col = st.columns([2, 1])
    
    with chat_col:
        # Chat section
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("💬 Conversation")
        
        # Display conversation history
        if st.session_state.conversation_history:
            for msg in st.session_state.conversation_history[-8:]:
                if msg['speaker'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {msg['message']}
                        <small style="float: right;">{msg['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    score_display = f" (Fluency: {msg['fluency_score']}/100)" if msg.get('fluency_score') else ""
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>{current_tutor['name']}:</strong> {msg['message']}{score_display}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("👋 Start a conversation with your tutor!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input section
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        # Voice Input Section
        st.subheader("🎤 Voice Input")
        voice_col1, voice_col2 = st.columns(2)
        
        # Initialize voice session state
        if 'last_recorded_text' not in st.session_state:
            st.session_state.last_recorded_text = ""
        if 'voice_ready' not in st.session_state:
            st.session_state.voice_ready = False
        
        with voice_col1:
            if st.button("🎤 Start Recording", use_container_width=True):
                try:
                    import speech_recognition as sr
                    st.session_state.voice_ready = True
                    
                    with st.spinner("🎤 Recording... Speak now!"):
                        r = sr.Recognizer()
                        with sr.Microphone() as source:
                            st.write("🔴 Recording... Speak clearly!")
                            audio = r.listen(source, timeout=5, phrase_time_limit=10)
                        
                        # Convert speech to text
                        text = r.recognize_google(audio)
                        st.session_state.last_recorded_text = text
                        st.success(f"✅ Recorded: {text}")
                        
                except ImportError:
                    st.error("❌ Voice libraries not installed!")
                    st.code("pip install speechrecognition pyaudio")
                except Exception as e:
                    st.error(f"❌ Recording failed: {str(e)}")
                    st.info("Make sure microphone permission is granted!")
        
        with voice_col2:
            if st.session_state.last_recorded_text and st.button("📤 Send Recording", use_container_width=True):
                # Process recorded message
                user_message = st.session_state.last_recorded_text
                
                # Add to conversation
                st.session_state.conversation_history.append({
                    'speaker': 'user',
                    'message': user_message,
                    'timestamp': datetime.now().strftime("%H:%M")
                })
                
                # Get AI response
                ai_response, fluency_score = get_ai_response(user_message, st.session_state.current_tutor)
                
                # Add AI response
                st.session_state.conversation_history.append({
                    'speaker': 'ai',
                    'message': ai_response,
                    'timestamp': datetime.now().strftime("%H:%M"),
                    'fluency_score': fluency_score
                })
                
                st.session_state.total_conversations += 1
                st.session_state.last_recorded_text = ""  # Clear recorded text
                
                # Try to speak response
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 150)
                    engine.say(ai_response)
                    engine.runAndWait()
                except:
                    pass  # Silent fail if TTS not available
                
                st.rerun()
        
        # Display recorded text
        if st.session_state.last_recorded_text:
            st.info(f"🎤 Recorded: {st.session_state.last_recorded_text}")
        
        # Voice setup instructions
        if not st.session_state.voice_ready:
            with st.expander("🎤 Voice Setup Instructions"):
                st.write("**Install voice libraries:**")
                st.code("pip install speechrecognition pyttsx3 pyaudio")
                st.write("**For macOS:**")
                st.code("brew install portaudio")
                st.write("**Grant microphone permission** in System Preferences → Security & Privacy → Microphone")
        
        st.write("---")
        st.subheader("⌨️ Type Your Message")
        
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Your message:",
                placeholder=f"Type your message for {current_tutor['name']}..."
            )
            submit_button = st.form_submit_button("📤 Send Message", use_container_width=True)
            
            if submit_button and user_input.strip():
                # Add user message
                st.session_state.conversation_history.append({
                    'speaker': 'user',
                    'message': user_input.strip(),
                    'timestamp': datetime.now().strftime("%H:%M")
                })
                
                # Get AI response
                ai_response, fluency_score = get_ai_response(user_input.strip(), st.session_state.current_tutor)
                
                # Add AI response
                st.session_state.conversation_history.append({
                    'speaker': 'ai',
                    'message': ai_response,
                    'timestamp': datetime.now().strftime("%H:%M"),
                    'fluency_score': fluency_score
                })
                
                st.session_state.total_conversations += 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with avatar_col:
        # Avatar section
        st.markdown(f"""
        <div class="avatar-display" style="background: linear-gradient(45deg, {current_tutor['color']}, {current_tutor['color']}aa);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
            <h3>{current_tutor['name']}</h3>
            <p><strong>{current_tutor['language']}</strong></p>
            <p>{current_tutor['personality']}</p>
            <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 10px; margin-top: 1rem;">
                Status: Ready to chat!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress section
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📊 Your Progress")
        
        if st.session_state.total_conversations > 0:
            st.write(f"**Total Conversations:** {st.session_state.total_conversations}")
            st.write(f"**Messages Exchanged:** {len(st.session_state.conversation_history)}")
            
            # Calculate average score
            scores = [msg.get('fluency_score', 0) for msg in st.session_state.conversation_history if msg.get('fluency_score')]
            if scores:
                avg_score = sum(scores) / len(scores)
                st.write(f"**Average Fluency:** {avg_score:.1f}/100")
        else:
            st.write("Start chatting to see your progress!")
        
        st.write("---")
        
        # Quick actions
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.conversation_history = []
            st.success("✅ New session started!")
            time.sleep(1)
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_page = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main application logic
def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        if st.session_state.current_page == 'tutor_selection':
            show_tutor_selection()
        else:
            show_main_chat()

    if __name__ == "__main__":
        main()