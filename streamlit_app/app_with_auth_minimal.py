import streamlit as st
import time

# Page config
st.set_page_config(
    page_title="Vakta AI",
    page_icon="🎭",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def show_login():
    st.title("🎭 Vakta AI")
    st.markdown("### Language Learning Platform")
    
    if st.button("🚀 Start Demo", type="primary"):
        st.session_state.authenticated = True
        st.success("Welcome!")
        time.sleep(1)
        st.rerun()

def show_main():
    st.markdown("# 🎭 Vakta AI Working!")
    
    st.markdown("""
    <div style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; 
                padding: 2rem; border-radius: 15px; text-align: center;">
        <h2>✅ Application is Working!</h2>
        <p>Ready Player Me integration coming next...</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        show_main()

if __name__ == "__main__":
    main()
