# streamlit_app.py

import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Vakta AI Chat", page_icon="🗣️")
st.title("🗣️ Vakta AI – Practice Your Language Skills")

# Session state for token
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# Registration Form
with st.expander("📝 New here? Register"):
    st.subheader("Create a new account")
    reg_username = st.text_input("Username", key="reg_user")
    reg_email = st.text_input("Email")
    reg_fullname = st.text_input("Full Name")
    reg_password = st.text_input("Password", type="password", key="reg_pass")
    reg_primary = st.text_input("Primary Language (e.g. Hindi)")
    reg_target = st.text_input("Target Language (e.g. English)")

    if st.button("Register"):
        payload = {
            "username": reg_username,
            "email": reg_email,
            "full_name": reg_fullname,
            "password": reg_password,
            "primary_language": reg_primary,
            "target_language": reg_target
        }
        try:
            res = requests.post(f"{BASE_URL}/register", json=payload)
            if res.status_code == 200:
                st.success("Registration successful! Please login.")
            else:
                st.error(f"Registration failed: {res.json()['detail']}")
        except Exception as e:
            st.error(f"Error: {e}")

# Login Form
st.subheader("🔐 Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        res = requests.post(
            f"{BASE_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if res.status_code == 200:
            st.session_state.access_token = res.json()["access_token"]
            st.success("Login successful!")
        else:
            st.error("Login failed. Please check your credentials.")
    except Exception as e:
        st.error(f"Error: {e}")

# If logged in, show chat UI
if st.session_state.access_token:
    st.markdown("---")
    st.subheader("💬 Chat with Vakta AI")

    user_input = st.text_input("Your sentence:", placeholder="Type something...")

    if st.button("Send"):
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        payload = {"user_input_text": user_input}

        try:
            res = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                st.success(f"AI: {data['ai_response']}")
                st.info(f"🧠 Fluency Score: {data['fluency_score']}")
            else:
                st.error(f"Error: {res.json()['detail']}")
        except Exception as e:
            st.error(f"Error: {e}")
