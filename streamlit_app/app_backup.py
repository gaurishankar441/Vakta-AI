import streamlit as st
import time
import random

st.set_page_config(page_title="🎭 Vakta AI", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.card { background: white; padding: 2rem; border-radius: 15px; margin: 2rem auto; max-width: 600px; }
.chat-msg { padding: 1rem; margin: 0.5rem 0; border-radius: 10px; }
.user-msg { background: #4ECDC4; color: white; }
.ai-msg { background: #667eea; color: white; }
</style>
""", unsafe_allow_html=True)

# Session state
if "auth" not in st.session_state:
    st.session_state.auth = False
if "conversations" not in st.session_state:
    st.session_state.conversations = []

# Enhanced AI responses
def get_smart_response(user_input):
    user_lower = user_input.lower()
    
    # Different response types based on input
    if any(word in user_lower for word in ['hi', 'hello', 'namaste']):
        responses = [
            "Namaste! Main Priya hun. Bahut khushi hui aapko dekhkar!",
            "Hello! Welcome! Aaj kya sikhenge together?",
            "Hi there! Ready for some Hindi-English practice?"
        ]
    elif any(word in user_lower for word in ['learn', 'study', 'practice']):
        responses = [
            "Wah! Learning ka enthusiasm dekh kar maja aa gaya!",
            "Bilkul! Practice makes perfect. Main help karungi!",
            "Excellent! Sikhne ka josh bahut accha hai!"
        ]
    elif any(word in user_lower for word in ['good', 'great', 'nice', 'awesome']):
        responses = [
            "Bahut accha! Aapka positive attitude amazing hai!",
            "Shabash! Keep this energy up!",
            "Perfect! Ye confidence language learning mein helpful hai!"
        ]
    elif any(word in user_lower for word in ['how', 'what', 'why', 'when']):
        responses = [
            f"Accha question! '{user_input}' ke baare mein batata hun...",
            f"Interesting! Aapne poocha '{user_input}' - ye important topic hai!",
            f"Good thinking! '{user_input}' ka answer context pe depend karta hai."
        ]
    else:
        responses = [
            f"Interesting! Aapne kaha '{user_input}' - tell me more!",
            f"Accha! '{user_input}' ke baare mein aur explain kar sakte hain?",
            f"Good point! '{user_input}' shows you're thinking deeply!",
            f"Bahut badhiya! '{user_input}' - aise conversations helpful hain!"
        ]
    
    response = random.choice(responses)
    fluency_score = random.randint(70, 95)
    
    return response, fluency_score

# Login page
if not st.session_state.auth:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🎭 Vakta AI")
    st.write("Language Learning Platform")
    st.write("**Features:** AI Tutor Priya, Smart Responses, Progress Tracking")
    if st.button("🚀 Start Learning"):
        st.session_state.auth = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Main app
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🎭 Learning with Priya")
    
    # Show conversation history
    if st.session_state.conversations:
        st.subheader("💬 Conversation History")
        for conv in st.session_state.conversations[-5:]:  # Show last 5
            st.markdown(f'<div class="chat-msg user-msg">You: {conv["user"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-msg ai-msg">Priya: {conv["ai"]} (Score: {conv["score"]}/100)</div>', unsafe_allow_html=True)
    
    st.write("---")
    
    # Input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message:")
        submit = st.form_submit_button("📤 Send")
        
        if submit and user_input:
            # Get smart AI response
            ai_response, score = get_smart_response(user_input)
            
            # Add to conversation history
            st.session_state.conversations.append({
                "user": user_input,
                "ai": ai_response,
                "score": score
            })
            
            st.success(f"✅ Message sent! Fluency Score: {score}/100")
            st.rerun()
    
    # Stats
    if st.session_state.conversations:
        total = len(st.session_state.conversations)
        avg_score = sum(c["score"] for c in st.session_state.conversations) / total
        st.write(f"**Stats:** {total} conversations, Average: {avg_score:.1f}/100")
    
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
