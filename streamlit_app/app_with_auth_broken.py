# Copy the "Debug Version - No CSS/HTML Components" code from above
import streamlit as st
import streamlit.components.v1 as components
import time
import json
import random
from datetime import datetime
import re

# Page config
st.set_page_config(
    page_title="🎭 Vakta AI - Language Learning Platform",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main > div {
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 3rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
        max-width: 500px;
        margin: 2rem auto;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #4ECDC4;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .message-user {
        background: linear-gradient(45deg, #4ECDC4, #44A08D);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .message-ai {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .avatar-container {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        min-height: 350px;
    }
    
    .tutor-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s ease;
        border: 2px solid transparent;
    }
    
    .tutor-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .tutor-selected {
        border: 2px solid #4ECDC4;
        transform: translateY(-3px);
    }
    
    .voice-controls {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .progress-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'authenticated': False,
        'current_tutor': 'priya',
        'conversation_history': [],
        'total_conversations': 0,
        'fluency_scores': [],
        'current_page': 'login',
        'voice_recording': False,
        'last_recorded_text': '',
        'avatar_expression': 'neutral',
        'user_progress': {
            'level': 'Beginner',
            'sessions_completed': 0,
            'total_words_learned': 0,
            'streak_days': 1
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Tutor configurations
TUTORS = {
    'priya': {
        'name': 'Priya',
        'language': 'Hindi/English',
        'personality': 'Friendly and patient, specializes in conversational practice',
        'color': '#FF6B6B',
        'accent_color': '#FF8E8E',
        'avatar_style': 'warm',
        'greeting': 'Namaste! Main Priya hun. Aaj kya sikhenge?'
    },
    'alex': {
        'name': 'Alex',
        'language': 'English',
        'personality': 'Professional and structured, focuses on grammar and business English',
        'color': '#4ECDC4',
        'accent_color': '#7DDDD9',
        'avatar_style': 'professional',
        'greeting': 'Hello! I\'m Alex. Ready to improve your English skills?'
    },
    'maya': {
        'name': 'Maya',
        'language': 'Spanish/English',
        'personality': 'Energetic and creative, loves cultural learning and storytelling',
        'color': '#A8E6CF',
        'accent_color': '#88D8A3',
        'avatar_style': 'creative',
        'greeting': '¡Hola! Soy Maya. Let\'s explore languages together!'
    }
}

# Voice functionality with error handling
def init_voice_system():
    """Initialize voice recognition and TTS systems"""
    try:
        import speech_recognition as sr
        import pyttsx3
        return True, "Voice system ready"
    except ImportError as e:
        return False, f"Voice libraries not installed: {str(e)}"
    except Exception as e:
        return False, f"Voice system error: {str(e)}"

def get_voice_input():
    """Get voice input from microphone"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            st.write("🎤 Listening... Speak now!")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        
        text = r.recognize_google(audio)
        return True, text
    except ImportError:
        return False, "Speech recognition not installed. Run: pip install speechrecognition pyaudio"
    except sr.UnknownValueError:
        return False, "Could not understand audio. Please try again."
    except sr.RequestError as e:
        return False, f"Could not request results: {e}"
    except Exception as e:
        return False, f"Voice input error: {e}"

def speak_text(text, tutor_voice="default"):
    """Convert text to speech"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Set voice properties based on tutor
        voices = engine.getProperty('voices')
        if tutor_voice == "priya" and len(voices) > 1:
            engine.setProperty('voice', voices[1].id)  # Female voice
        elif tutor_voice == "alex" and len(voices) > 0:
            engine.setProperty('voice', voices[0].id)  # Male voice
        elif tutor_voice == "maya" and len(voices) > 1:
            engine.setProperty('voice', voices[1].id)  # Female voice
        
        engine.setProperty('rate', 150)  # Speaking rate
        engine.say(text)
        engine.runAndWait()
        return True
    except ImportError:
        return False
    except Exception as e:
        st.error(f"TTS error: {e}")
        return False

# 3D Avatar Component with Enhanced Features
def render_3d_avatar(tutor_key, expression="neutral", is_speaking=False):
    """Render 3D avatar with Three.js"""
    tutor = TUTORS[tutor_key]
    
    avatar_html = f"""
    <div style="width: 100%; height: 350px; border-radius: 15px; overflow: hidden; background: linear-gradient(45deg, {tutor['color']}, {tutor['accent_color']});">
        <div id="avatar-container-{tutor_key}" style="width: 100%; height: 100%; position: relative;">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script>
                // Create 3D scene for tutor {tutor['name']}
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                
                const container = document.getElementById('avatar-container-{tutor_key}');
                if (container) {{
                    renderer.setSize(container.offsetWidth, container.offsetHeight);
                    renderer.setClearColor(0x000000, 0);
                    container.appendChild(renderer.domElement);
                    
                    // Enhanced lighting system
                    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                    scene.add(ambientLight);
                    
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(1, 1, 1);
                    scene.add(directionalLight);
                    
                    const pointLight = new THREE.PointLight(0x{tutor['color'][1:]}, 0.5, 10);
                    pointLight.position.set(0, 2, 2);
                    scene.add(pointLight);
                    
                    // Create enhanced avatar geometry
                    const headGeometry = new THREE.SphereGeometry(0.8, 32, 32);
                    const bodyGeometry = new THREE.CylinderGeometry(0.6, 0.8, 1.5, 16);
                    
                    // Enhanced materials with better textures
                    const headMaterial = new THREE.MeshPhongMaterial({{ 
                        color: 0x{tutor['color'][1:]},
                        shininess: 30,
                        transparent: true,
                        opacity: 0.9
                    }});
                    
                    const bodyMaterial = new THREE.MeshPhongMaterial({{ 
                        color: 0x{tutor['accent_color'][1:]},
                        shininess: 20
                    }});
                    
                    // Create avatar meshes
                    const head = new THREE.Mesh(headGeometry, headMaterial);
                    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
                    
                    head.position.y = 1.2;
                    body.position.y = 0;
                    
                    // Create avatar group
                    const avatar = new THREE.Group();
                    avatar.add(head);
                    avatar.add(body);
                    scene.add(avatar);
                    
                    camera.position.z = 4;
                    camera.position.y = 0.5;
                    
                    // Expression and animation variables
                    let breathingPhase = 0;
                    let expressionIntensity = {'excited' if expression == 'excited' else 'normal'};
                    let speakingAnimation = {is_speaking};
                    
                    // Enhanced animation loop
                    function animate() {{
                        requestAnimationFrame(animate);
                        
                        // Breathing animation
                        breathingPhase += 0.02;
                        const breathScale = 1 + Math.sin(breathingPhase) * 0.05;
                        body.scale.set(1, breathScale, 1);
                        
                        // Expression-based animations
                        if (expressionIntensity === 'excited') {{
                            head.rotation.y = Math.sin(breathingPhase * 2) * 0.1;
                            const glowIntensity = 0.8 + Math.sin(breathingPhase * 3) * 0.2;
                            pointLight.intensity = glowIntensity;
                        }}
                        
                        // Speaking animation
                        if (speakingAnimation) {{
                            const speakPhase = breathingPhase * 4;
                            head.scale.set(1, 1 + Math.sin(speakPhase) * 0.03, 1);
                        }}
                        
                        // Gentle rotation
                        avatar.rotation.y += 0.005;
                        
                        renderer.render(scene, camera);
                    }}
                    
                    animate();
                    
                    // Handle window resize
                    window.addEventListener('resize', () => {{
                        if (container) {{
                            camera.aspect = container.offsetWidth / container.offsetHeight;
                            camera.updateProjectionMatrix();
                            renderer.setSize(container.offsetWidth, container.offsetHeight);
                        }}
                    }});
                }}
            </script>
        </div>
        
        <div style="position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); 
                    background: rgba(0,0,0,0.7); color: white; padding: 0.5rem 1rem; 
                    border-radius: 20px; font-size: 0.9rem;">
            <strong>{tutor['name']}</strong> • {expression.title()} • {tutor['language']}
        </div>
    </div>
    """
    
    components.html(avatar_html, height=350)

# AI Response System (Fixed to prevent HTML display)
def get_ai_response(user_input, tutor_key):
    """Generate AI response based on tutor personality"""
    tutor = TUTORS[tutor_key]
    
    # Clean the user input
    user_input = user_input.strip()
    
    # Simple AI responses based on tutor personality
    responses = {
        'priya': [
            f"Bahut accha! '{user_input}' - ye bilkul sahi hai. Aur practice karte rahiye!",
            f"Wah! Aapka pronunciation improve ho raha hai. '{user_input}' perfect tha!",
            f"Shabash! Main dekh sakti hun ki aap mehnat kar rahe hain. Keep it up!",
            f"Excellent effort! Aapke confidence mein improvement aa raha hai.",
        ],
        'alex': [
            f"Excellent work! Your pronunciation of '{user_input}' shows great improvement.",
            f"Well done! I can see your fluency developing. Keep practicing!",
            f"Outstanding! Your grammar structure is becoming more natural.",
            f"Impressive progress! Your confidence in speaking is clearly growing.",
        ],
        'maya': [
            f"¡Fantástico! Your energy in saying '{user_input}' is wonderful!",
            f"Amazing! I love how you're embracing the language learning journey!",
            f"Brilliant! Your creativity in expression is really showing through!",
            f"Wonderful! You're bringing such positive energy to our conversation!",
        ]
    }
    
    # Calculate fluency score
    fluency_score = min(95, max(65, len(user_input) * 2 + random.randint(10, 25)))
    
    # Select response based on tutor
    response = random.choice(responses[tutor_key])
    
    # Add encouragement based on score
    if fluency_score >= 85:
        response += " 🌟 Outstanding fluency!"
        expression = "excited"
    elif fluency_score >= 75:
        response += " 👍 Great job!"
        expression = "happy"
    else:
        response += " 💪 Keep practicing!"
        expression = "encouraging"
    
    return response, fluency_score, expression

def display_ai_response_fixed(response, tutor_key):
    """Display AI response without HTML tags"""
    # Clean any HTML tags from response
    clean_response = re.sub(r'<[^>]+>', '', response)
    
    st.markdown(f"""
    <div class="message-ai">
        <strong>{TUTORS[tutor_key]['name']}:</strong><br>
        {clean_response}
    </div>
    """, unsafe_allow_html=True)

# Login Page
def show_login():
    st.markdown("""
    <div class="login-container">
        <h1>🎭 Vakta AI</h1>
        <h3>Advanced Language Learning Platform</h3>
        <p style="font-size: 1.1rem; color: #666; margin: 1.5rem 0;">
            Master languages with AI-powered 3D tutors and immersive conversations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 3D AI Tutors</h4>
            <p>Interactive 3D avatars with realistic expressions and personalities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🗣️ Voice Learning</h4>
            <p>Speech recognition and pronunciation feedback in real-time</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Smart Progress</h4>
            <p>AI-powered fluency tracking and personalized learning paths</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo preview avatar
    st.markdown("### 🎭 Meet Your AI Tutors")
    render_3d_avatar('priya', 'excited')
    
    # Login button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Learning Journey", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.current_page = 'main'
            st.success("🎉 Welcome to Vakta AI!")
            time.sleep(1)
            st.rerun()

# Tutor Selection Page
def show_tutor_selection():
    st.markdown("## 🎭 Choose Your AI Tutor")
    
    cols = st.columns(3)
    
    for i, (tutor_key, tutor) in enumerate(TUTORS.items()):
        with cols[i]:
            # Tutor card styling
            selected_class = "tutor-selected" if st.session_state.current_tutor == tutor_key else ""
            
            st.markdown(f"""
            <div class="tutor-card {selected_class}" style="border-color: {tutor['color']};">
                <h4 style="color: {tutor['color']};">{tutor['name']}</h4>
                <p><strong>Specialty:</strong> {tutor['language']}</p>
                <p style="font-size: 0.9rem;">{tutor['personality']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Selection button
            if st.button(f"Select {tutor['name']}", key=f"select_{tutor_key}", use_container_width=True):
                st.session_state.current_tutor = tutor_key
                st.session_state.current_page = 'main'
                st.success(f"✅ {tutor['name']} selected!")
                
                # Add greeting to conversation
                greeting = tutor['greeting']
                st.session_state.conversation_history.append({
                    'speaker': 'ai',
                    'message': greeting,
                    'timestamp': datetime.now().strftime("%H:%M"),
                    'fluency_score': None
                })
                time.sleep(1)
                st.rerun()
            
            # Voice preview button
            if st.button(f"🎤 Voice Preview", key=f"preview_{tutor_key}"):
                with st.spinner("Loading voice preview..."):
                    success = speak_text(tutor['greeting'], tutor_key)
                    if success:
                        st.success("🔊 Voice preview played!")
                    else:
                        st.info("🔇 Install voice libraries for audio: pip install pyttsx3")

# Main Chat Interface
def show_main_chat():
    current_tutor = TUTORS[st.session_state.current_tutor]
    
    # Header with tutor info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## 🎭 Learning with {current_tutor['name']}")
    with col2:
        if st.button("🔄 Change Tutor"):
            st.session_state.current_page = 'tutor_selection'
            st.rerun()
    
    # Main layout
    chat_col, avatar_col = st.columns([2, 1])
    
    with avatar_col:
        st.markdown("### 3D Avatar")
        render_3d_avatar(
            st.session_state.current_tutor, 
            st.session_state.avatar_expression,
            False
        )
        
        # Avatar status
        st.markdown(f"""
        <div style="background: {current_tutor['color']}; color: white; padding: 0.5rem; 
                    border-radius: 10px; text-align: center; margin-top: 1rem;">
            <strong>{current_tutor['name']}</strong><br>
            <small>{current_tutor['language']} Specialist</small>
        </div>
        """, unsafe_allow_html=True)
    
    with chat_col:
        st.markdown("### 💬 Conversation")
        
        # Chat history
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Display conversation history
            for msg in st.session_state.conversation_history[-10:]:  # Show last 10 messages
                if msg['speaker'] == 'user':
                    st.markdown(f"""
                    <div class="message-user">
                        <strong>You:</strong> {msg['message']}
                        <small style="float: right;">{msg['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Use the fixed display function
                    display_ai_response_fixed(msg['message'], st.session_state.current_tutor)
                    if msg.get('fluency_score'):
                        st.markdown(f"""
                        <div style="text-align: right; font-size: 0.8rem; color: #666; margin-top: 0.2rem;">
                            Fluency Score: {msg['fluency_score']}/100
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Voice input section
        st.markdown("### 🎤 Voice Input")
        voice_col1, voice_col2 = st.columns(2)
        
        with voice_col1:
            if st.button("🎤 Start Recording", use_container_width=True):
                with st.spinner("🎤 Recording... Speak now!"):
                    success, result = get_voice_input()
                    if success:
                        st.session_state.last_recorded_text = result
                        st.success(f"✅ Recorded: {result}")
                    else:
                        st.error(f"❌ {result}")
        
        with voice_col2:
            if st.session_state.last_recorded_text and st.button("📤 Send Recording", use_container_width=True):
                process_user_message(st.session_state.last_recorded_text)
                st.session_state.last_recorded_text = ""
                st.rerun()
        
        # Display recorded text
        if st.session_state.last_recorded_text:
            st.info(f"🎤 Recorded: {st.session_state.last_recorded_text}")
        
        # Text input section
        st.markdown("### ⌨️ Type Your Message")
        
        # Text input form
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Your message:",
                placeholder=f"Type your message for {current_tutor['name']}...",
                key="user_input"
            )
            submit_button = st.form_submit_button("📤 Send", use_container_width=True)
            
            if submit_button and user_input.strip():
                process_user_message(user_input.strip())
                st.rerun()

def process_user_message(user_input):
    """Process user message and generate AI response"""
    # Add user message to history
    st.session_state.conversation_history.append({
        'speaker': 'user',
        'message': user_input,
        'timestamp': datetime.now().strftime("%H:%M"),
        'fluency_score': None
    })
    
    # Get AI response
    ai_response, fluency_score, expression = get_ai_response(user_input, st.session_state.current_tutor)
    
    # Update avatar expression
    st.session_state.avatar_expression = expression
    
    # Add AI response to history
    st.session_state.conversation_history.append({
        'speaker': 'ai',
        'message': ai_response,
        'timestamp': datetime.now().strftime("%H:%M"),
        'fluency_score': fluency_score
    })
    
    # Update progress
    st.session_state.total_conversations += 1
    st.session_state.fluency_scores.append(fluency_score)
    st.session_state.user_progress['sessions_completed'] += 1
    st.session_state.user_progress['total_words_learned'] += len(user_input.split())
    
    # Voice output
    speak_text(ai_response, st.session_state.current_tutor)

# Sidebar Progress Tracking
def show_sidebar():
    with st.sidebar:
        st.markdown("### 📊 Your Progress")
        
        # User stats
        progress = st.session_state.user_progress
        st.markdown(f"""
        <div class="progress-card">
            <strong>Level:</strong> {progress['level']}<br>
            <strong>Sessions:</strong> {progress['sessions_completed']}<br>
            <strong>Words Learned:</strong> {progress['total_words_learned']}<br>
            <strong>Streak:</strong> {progress['streak_days']} days
        </div>
        """, unsafe_allow_html=True)
        
        # Recent fluency scores
        if st.session_state.fluency_scores:
            avg_score = sum(st.session_state.fluency_scores[-5:]) / len(st.session_state.fluency_scores[-5:])
            st.markdown(f"""
            <div class="progress-card">
                <strong>Recent Average:</strong> {avg_score:.1f}/100<br>
                <strong>Total Conversations:</strong> {st.session_state.total_conversations}
            </div>
            """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = 'main'
            st.rerun()
        
        if st.button("🎭 Change Tutor", use_container_width=True):
            st.session_state.current_page = 'tutor_selection'
            st.rerun()
        
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.avatar_expression = 'neutral'
            st.success("✅ Session reset!")
            time.sleep(1)
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            # Reset session
            for key in ['authenticated', 'conversation_history', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # Voice system status
        st.markdown("### 🎤 Voice System")
        voice_ready, voice_msg = init_voice_system()
        if voice_ready:
            st.success("✅ Voice Ready")
        else:
            st.warning("⚠️ Voice Setup Needed")
            st.code("pip install speechrecognition pyttsx3 pyaudio")

# Main Application Logic
def main():
    init_session_state()
    
    # Route to appropriate page
    if not st.session_state.authenticated:
        show_login()
    else:
        # Show sidebar for authenticated users
        show_sidebar()
        
        # Route based on current page
        if st.session_state.current_page == 'tutor_selection':
            show_tutor_selection()
        else:
            show_main_chat()

# Run the application
    if __name__ == "__main__":
        main()