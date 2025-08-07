import streamlit as st
import time
import random
from datetime import datetime
import streamlit as st

st.title("HELLO WORLD")
st.write("Testing!")
st.set_page_config(page_title="🎭 Vakta AI", layout="wide")

# SAFE CSS - No content hiding
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.content-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login function
def show_login():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.title("🎭 Vakta AI")
    st.write("Language Learning Platform")
    if st.button("🚀 Start", type="primary"):
        st.session_state.authenticated = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Main function
def show_main():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.title("✅ Vakta AI Working!")
    st.write("🎉 Success! Application is working properly!")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Main app
if not st.session_state.authenticated:
    show_login()
else:
    show_main()
