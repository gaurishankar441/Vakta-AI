import streamlit as st
import time
import random

st.set_page_config(page_title="🎭 Vakta AI", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.card { background: white; padding: 2rem; border-radius: 15px; margin: 2rem auto; max-width: 600px; }
</style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div class=\"card\">", unsafe_allow_html=True)
    st.title("🎭 Vakta AI")
    st.write("Language Learning Platform")
    if st.button("🚀 Start"):
        st.session_state.auth = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class=\"card\">", unsafe_allow_html=True)
    st.title("✅ Vakta AI Working!")
    st.write("🎉 Application loaded successfully!")
    
    with st.form("chat"):
        msg = st.text_input("Type message:")
        if st.form_submit_button("Send") and msg:
            st.success(f"You said: {msg}")
    
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
