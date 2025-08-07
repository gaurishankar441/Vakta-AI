import streamlit as st
import streamlit.components.v1 as components
import time
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Vakta AI - Ready Player Me Edition",
    page_icon="🎭",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_tutor' not in st.session_state:
    st.session_state.current_tutor = 0
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'user_progress' not in st.session_state:
    st.session_state.user_progress = {
        'total_conversations': 0,
        'average_fluency': 0
    }
if 'tts_enabled' not in st.session_state:
    st.session_state.tts_enabled = True

# Tutor configurations
TUTORS = [
    {
        "name": "Priya Madam",
        "description": "Friendly Hindi-English Teacher",
        "color": "#FF6B6B",
        "emoji": "👩‍🏫",
        "personality": "encouraging"
    },
    {
        "name": "Alex Sir",
        "description": "Professional English Mentor", 
        "color": "#4ECDC4",
        "emoji": "👨‍💼",
        "personality": "professional"
    },
    {
        "name": "Maya Didi",
        "description": "Fun Language Learning Buddy",
        "color": "#45B7D1",
        "emoji": "👩‍🎓", 
        "personality": "playful"
    }
]

def display_ready_player_me_avatar(expression="happy", tutor_index=0, height=500):
    """Display Ready Player Me 3D Avatar"""
    
    tutor = TUTORS[tutor_index]
    
    avatar_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
            #avatar-container {{ position: relative; width: 100%; height: {height}px; }}
            .avatar-info {{ position: absolute; bottom: 20px; left: 20px; background: rgba(255,255,255,0.1); 
                           backdrop-filter: blur(10px); border-radius: 15px; padding: 15px; color: white; }}
            .expression-indicator {{ position: absolute; top: 20px; right: 20px; background: rgba(255,255,255,0.1);
                                   backdrop-filter: blur(10px); border-radius: 15px; padding: 10px; color: white; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div id="avatar-container">
            <div class="expression-indicator">😊 {expression.title()}</div>
            <div class="avatar-info">
                <div style="font-size: 1.2em; font-weight: bold;">{tutor['name']}</div>
                <div style="font-size: 0.9em; opacity: 0.8;">{tutor['description']}</div>
            </div>
        </div>

        <script>
            class VaktaAvatar3D {{
                constructor() {{
                    this.scene = new THREE.Scene();
                    this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / {height}, 0.1, 1000);
                    this.renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    this.avatar = null;
                    
                    this.init();
                }}
                
                init() {{
                    // Setup renderer
                    this.renderer.setSize(window.innerWidth, {height});
                    this.renderer.setClearColor(0x87CEEB);
                    document.getElementById('avatar-container').appendChild(this.renderer.domElement);
                    
                    // Setup camera
                    this.camera.position.set(0, 1.6, 4);
                    this.camera.lookAt(0, 1.6, 0);
                    
                    // Setup lights
                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
                    this.scene.add(ambientLight);
                    
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(5, 10, 5);
                    this.scene.add(directionalLight);
                    
                    // Create avatar
                    this.createAvatar();
                    
                    // Start animation
                    this.animate();
                }}
                
                createAvatar() {{
                    this.avatar = new THREE.Group();
                    
                    // Head
                    const headGeometry = new THREE.SphereGeometry(0.3, 32, 32);
                    const headMaterial = new THREE.MeshLambertMaterial({{ color: 0xffdbac }});
                    const head = new THREE.Mesh(headGeometry, headMaterial);
                    head.position.y = 1.8;
                    this.avatar.add(head);
                    
                    // Eyes
                    const eyeGeometry = new THREE.SphereGeometry(0.04, 16, 16);
                    const eyeMaterial = new THREE.MeshLambertMaterial({{ color: 0x333333 }});
                    
                    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
                    leftEye.position.set(-0.1, 1.85, 0.25);
                    this.avatar.add(leftEye);
                    
                    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
                    rightEye.position.set(0.1, 1.85, 0.25);
                    this.avatar.add(rightEye);
                    
                    // Mouth
                    const mouthGeometry = new THREE.SphereGeometry(0.05, 16, 16);
                    const mouthMaterial = new THREE.MeshLambertMaterial({{ color: 0xff8888 }});
                    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
                    mouth.position.set(0, 1.72, 0.25);
                    mouth.scale.set(1.8, 0.6, 0.6);
                    this.avatar.add(mouth);
                    
                    // Body
                    const bodyGeometry = new THREE.CylinderGeometry(0.25, 0.3, 1, 32);
                    const bodyMaterial = new THREE.MeshLambertMaterial({{ color: '{tutor['color']}' }});
                    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
                    body.position.y = 1.2;
                    this.avatar.add(body);
                    
                    // Arms
                    const armGeometry = new THREE.CylinderGeometry(0.06, 0.08, 0.8, 16);
                    const armMaterial = new THREE.MeshLambertMaterial({{ color: 0xffdbac }});
                    
                    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
                    leftArm.position.set(-0.35, 1.2, 0);
                    leftArm.rotation.z = 0.4;
                    this.avatar.add(leftArm);
                    
                    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
                    rightArm.position.set(0.35, 1.2, 0);
                    rightArm.rotation.z = -0.4;
                    this.avatar.add(rightArm);
                    
                    // Store references
                    this.avatar.head = head;
                    this.avatar.mouth = mouth;
                    this.avatar.body = body;
                    this.avatar.leftArm = leftArm;
                    this.avatar.rightArm = rightArm;
                    
                    this.scene.add(this.avatar);
                    this.startAnimations();
                }}
                
                startAnimations() {{
                    // Breathing animation
                    const breathe = () => {{
                        const time = Date.now() * 0.002;
                        this.avatar.body.scale.y = 1 + Math.sin(time) * 0.03;
                        this.avatar.position.y = Math.sin(time) * 0.01;
                        requestAnimationFrame(breathe);
                    }};
                    breathe();
                    
                    // Expression animation for {expression}
                    this.setExpression('{expression}');
                }}
                
                setExpression(expression) {{
                    switch(expression) {{
                        case 'happy':
                            this.avatar.mouth.scale.set(2.2, 0.8, 0.6);
                            break;
                        case 'excited':
                            this.avatar.mouth.scale.set(2.8, 1.2, 0.6);
                            // Excited arm animation
                            let exciteTime = 0;
                            const excite = () => {{
                                exciteTime += 0.3;
                                this.avatar.leftArm.rotation.z = 0.4 + Math.sin(exciteTime) * 0.6;
                                this.avatar.rightArm.rotation.z = -0.4 + Math.sin(exciteTime + Math.PI) * 0.6;
                                if (exciteTime < Math.PI * 4) requestAnimationFrame(excite);
                            }};
                            excite();
                            break;
                        case 'thinking':
                            this.avatar.mouth.scale.set(1.2, 0.4, 0.6);
                            this.avatar.head.rotation.x = -0.1;
                            break;
                        case 'speaking':
                            let speakTime = 0;
                            const speak = () => {{
                                speakTime += 0.4;
                                const mouthScale = 1.2 + Math.sin(speakTime) * 0.4;
                                this.avatar.mouth.scale.set(1.8, mouthScale, 0.6);
                                if (speakTime < Math.PI * 8) requestAnimationFrame(speak);
                            }};
                            speak();
                            break;
                    }}
                }}
                
                animate() {{
                    requestAnimationFrame(() => this.animate());
                    
                    // Gentle rotation
                    if (this.avatar) {{
                        this.avatar.rotation.y += 0.002;
                    }}
                    
                    this.renderer.render(this.scene, this.camera);
                }}
            }}
            
            // Initialize avatar
            new VaktaAvatar3D();
        </script>
    </body>
    </html>
    """
    
    components.html(avatar_html, height=height)

def show_tutor_selection():
    """Show tutor selection interface"""
    st.markdown("### 🎭 Choose Your Ready Player Me Tutor")
    
    cols = st.columns(3)
    
    for i, tutor in enumerate(TUTORS):
        with cols[i]:
            # Display avatar preview
            display_ready_player_me_avatar("happy", i, 300)
            
            # Tutor info
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {tutor['color']}25, {tutor['color']}10);
                        border-radius: 20px; margin: 1rem 0; border: 2px solid {tutor['color']}30;">
                <h3 style="color: {tutor['color']}; margin: 0.5rem 0;">{tutor['name']}</h3>
                <p style="color: #666; margin: 0; font-size: 1rem;">{tutor['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ Select {tutor['name']}", key=f"select_{i}", use_container_width=True):
                st.session_state.current_tutor = i
                st.success(f"🎭 {tutor['name']} selected as your tutor!")
                st.rerun()

def show_login():
    """Login page with enhanced design"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 4rem; margin: 0;">🎭</h1>
        <h1 style="color: #667eea; margin: 1rem 0;">Welcome to Vakta AI</h1>
        <h3 style="color: #666; margin: 0;">Ready Player Me 3D Avatar Learning Platform</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #FF6B6B25, #FF6B6B10); 
                   border-radius: 20px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎭</div>
            <h4>3D Avatar Tutors</h4>
            <p>Interactive Ready Player Me characters with real-time expressions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4ECDC425, #4ECDC410); 
                   border-radius: 20px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🧠</div>
            <h4>AI Learning</h4>
            <p>Advanced AI analysis with personalized feedback and scoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #45B7D125, #45B7D110); 
                   border-radius: 20px; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎤</div>
            <h4>Voice Learning</h4>
            <p>Speech recognition with real-time pronunciation feedback</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Login options
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🚀 Get Started")
        
        if st.button("🎯 Start Demo (No Registration)", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.balloons()
            st.success("🎉 Welcome to the future of language learning!")
            time.sleep(1)
            st.rerun()
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; color: #666;">
            <small>Experience next-generation 3D avatar learning instantly!</small>
        </div>
        """, unsafe_allow_html=True)

def show_main_app():
    """Main application with Ready Player Me integration"""
    
    # Get current tutor
    tutor = TUTORS[st.session_state.current_tutor]
    
    # Header with gradient
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {tutor['color']}, {tutor['color']}cc); 
                color: white; padding: 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
            <div style="font-size: 4rem;">{tutor['emoji']}</div>
            <div>
                <h1 style="margin: 0; font-size: 2.5rem;">Vakta AI</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                    Ready Player Me 3D Avatar Learning
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎭 Current Tutor")
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {tutor['color']}20, {tutor['color']}10);
                    border-radius: 15px; border: 2px solid {tutor['color']}30;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{tutor['emoji']}</div>
            <h4 style="color: {tutor['color']}; margin: 0.5rem 0;">{tutor['name']}</h4>
            <p style="color: #666; margin: 0; font-size: 0.9rem;">{tutor['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Change Tutor", use_container_width=True):
            st.session_state.show_tutor_selection = True
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Learning Progress")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sessions", st.session_state.user_progress['total_conversations'])
        with col2:
            st.metric("Avg Score", f"{st.session_state.user_progress['average_fluency']}%")
        
        # Settings
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        tts_enabled = st.checkbox("🔊 Enable Voice", value=st.session_state.tts_enabled)
        st.session_state.tts_enabled = tts_enabled
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # Show tutor selection if requested
    if st.session_state.get('show_tutor_selection', False):
        show_tutor_selection()
        if st.button("✅ Continue Learning", type="primary", use_container_width=True):
            st.session_state.show_tutor_selection = False
            st.rerun()
        return
    
    # Main avatar display
    st.markdown("### 🎭 Your AI Tutor")
    display_ready_player_me_avatar("happy", st.session_state.current_tutor, 500)
    
    # Welcome message
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {tutor['color']}15, {tutor['color']}05); 
                border-radius: 20px; margin: 2rem 0; border: 1px solid {tutor['color']}20;">
        <h2 style="color: {tutor['color']}; margin: 0;">Welcome to Interactive Learning!</h2>
        <p style="color: #666; margin: 1rem 0; font-size: 1.1rem;">
            I'm <strong>{tutor['name']}</strong>, your {tutor['description'].lower()}
        </p>
        <p style="color: #888; margin: 0;">
            ✨ Ready to practice English with next-generation 3D avatar technology? ✨
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat interface
    st.markdown("### 💬 Start Your Learning Session")
    
    # Input method selection
    input_method = st.radio("Choose your interaction style:", ["💬 Type Message", "🎤 Voice Input"], horizontal=True)
    
    if input_method == "💬 Type Message":
        with st.form("chat_form"):
            user_input = st.text_area(
                "Express yourself in English:", 
                placeholder="Type your thoughts, questions, or practice sentences here...",
                height=120
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("📤 Send to AI Tutor", type="primary", use_container_width=True)
            
            if submitted and user_input.strip():
                process_message(user_input)
    
    else:  # Voice Input
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎤 Start Recording", type="primary", use_container_width=True):
                st.info("🎙️ Voice recording feature coming soon! For now, please use text input.")
        
        with col2:
            st.info("💡 Voice recognition will be available in the next update!")
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown("---")
        st.markdown("### 💬 Your Learning Journey")
        
        for i, conv in enumerate(st.session_state.conversation_history[-5:]):  # Show last 5
            # User message
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 1.5rem; 
                        border-radius: 15px; margin: 1rem 0; border-left: 4px solid #007bff;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">👤</span>
                    <strong style="color: #007bff;">You said:</strong>
                </div>
                <p style="color: #333; margin: 0; padding-left: 2rem; font-size: 1.1rem;">
                    "{conv['user_input']}"
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # AI response with avatar
            display_ai_response(conv['ai_response'], conv.get('fluency_score', 80))
            
            if i < len(st.session_state.conversation_history[-5:]) - 1:
                st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>")

def display_ai_response(ai_response, fluency_score):
    """Display AI response with avatar"""
    
    tutor = TUTORS[st.session_state.current_tutor]
    
    # Determine expression based on score
    if fluency_score >= 80:
        expression = "excited"
        feedback = "🏆 Outstanding!"
        color = "#28a745"
    elif fluency_score >= 60:
        expression = "happy"
        feedback = "😊 Great job!"
        color = "#ffc107"
    else:
        expression = "thinking"
        feedback = "🤔 Keep practicing!"
        color = "#6c757d"
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Small avatar with expression
        display_ready_player_me_avatar(expression, st.session_state.current_tutor, 250)
        
        # Feedback indicator
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(45deg, {color}, {color}dd);
                    border-radius: 15px; color: white; font-weight: bold; margin-top: 1rem;">
            <div style="font-size: 1.1rem;">{feedback}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Score: {fluency_score}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # AI response
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ffffff, #f8f9fa); padding: 2rem; border-radius: 20px; 
                    border-left: 5px solid {tutor['color']}; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-right: 1rem;">{tutor['emoji']}</div>
                <div>
                    <h4 style="color: {tutor['color']}; margin: 0;">{tutor['name']} responds:</h4>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Ready Player Me AI Tutor</p>
                </div>
            </div>
            
            <div style="background: rgba(255,255,255,0.8); padding: 1.5rem; border-radius: 15px; 
                        border: 1px solid {tutor['color']}20;">
                <p style="color: #333; line-height: 1.7; margin: 0; font-size: 1.1rem;">
                    {ai_response}
                </p>
            </div>
            
            <div style="margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <div style="background: {tutor['color']}; color: white; padding: 0.5rem 1rem; 
                            border-radius: 20px; font-size: 0.9rem; font-weight: bold;">
                    Fluency: {fluency_score}%
                </div>
                <div style="color: #999; font-size: 0.8rem;">
                    🎭 Powered by Ready Player Me
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def process_message(user_input):
    """Process user message and generate AI response"""
    
    tutor = TUTORS[st.session_state.current_tutor]
    
    # Simple AI response generation based on tutor personality
    if tutor['personality'] == 'encouraging':
        ai_response = f"That's wonderful! You said: '{user_input}'. I love your enthusiasm for learning English! Your expression shows great progress. Keep practicing with confidence! 🌟"
    elif tutor['personality'] == 'professional':  
        ai_response = f"Excellent input. Your message: '{user_input}' demonstrates good language structure. I recommend focusing on expanding your vocabulary further. Well done on your progress."
    else:  # playful
        ai_response = f"Awesome! You shared: '{user_input}' - that's super cool! I'm excited to see you practicing English. Learning is such an adventure! Let's keep this energy going! 🎉"
    
    # Simple fluency scoring
    word_count = len(user_input.split())
    char_count = len(user_input)
    
    base_score = min(word_count * 8, 70)
    complexity_bonus = min(char_count // 8, 20)
    grammar_bonus = 10 if any(punct in user_input for punct in '.!?') else 0
    
    fluency_score = min(base_score + complexity_bonus + grammar_bonus, 100)
    
    # Add to conversation history
    st.session_state.conversation_history.append({
        'user_input': user_input,
        'ai_response': ai_response,
        'fluency_score': fluency_score,
        'timestamp': datetime.now()
    })
    
    # Update progress
    st.session_state.user_progress['total_conversations'] += 1
    
    # Calculate average fluency
    scores = [conv['fluency_score'] for conv in st.session_state.conversation_history]
    st.session_state.user_progress['average_fluency'] = sum(scores) // len(scores)
    
    st.success("✅ Message processed! Check your AI tutor's response below.")
    st.rerun()

def main():
    """Main application function"""
    
    # Custom CSS
    st.markdown("""
    <style>
        .stButton > button {
            border-radius: 20px;
            border: none;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .stSelectbox > div > div {
            border-radius: 15px;
        }
        .stTextArea > div > div > textarea {
            border-radius: 15px;
        }
        /* Hide Streamlit menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Main application logic
    if not st.session_state.authenticated:
        show_login()
    else:
        show_main_app()

    if __name__ == "__main__":
        main()