# streamlit_app/app_with_auth.py

import streamlit as st
import requests
import json
from datetime import datetime

# Backend API base URL
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def make_api_request(endpoint, method="GET", data=None, auth_required=False):
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth_required and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "GET":
            response = requests.get(url, headers=headers)
        else:
            return {"error": "Unsupported method"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}

def send_chat_message(message):
    """Send chat message to AI"""
    data = {"message": message}  # FIXED: Changed from user_input_text to message
    return make_api_request("/chat", method="POST", data=data, auth_required=True)

def show_login_page():
    """Display login/register interface"""
    st.title("🗣️ Vakta AI – Practice Your Language Skills")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username and password:
                    # Prepare login data
                    login_data = {
                        "username": username,
                        "password": password
                    }
                    
                    # Make login request
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/token",
                            data=login_data,
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            token_data = response.json()
                            st.session_state.access_token = token_data["access_token"]
                            st.session_state.authenticated = True
                            
                            # Get user info
                            user_response = make_api_request("/users/me", auth_required=True)
                            if "error" not in user_response:
                                st.session_state.user_info = user_response
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Failed to get user info")
                        else:
                            st.error("Invalid credentials")
                    except requests.exceptions.RequestException:
                        st.error("Connection error. Please check if backend is running.")
                else:
                    st.error("Please fill all fields")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_full_name = st.text_input("Full Name", key="reg_full_name")
            new_password = st.text_input("Password", type="password", key="reg_password")
            primary_language = st.selectbox("Primary Language", ["Hindi", "English", "Spanish", "French"])
            target_language = st.selectbox("Target Language", ["English", "Hindi", "Spanish", "French"])
            register_button = st.form_submit_button("Create Account")
            
            if register_button:
                if all([new_username, new_email, new_full_name, new_password]):
                    register_data = {
                        "username": new_username,
                        "email": new_email,
                        "full_name": new_full_name,
                        "password": new_password,
                        "primary_language": primary_language.lower()[:2],
                        "target_language": target_language.lower()[:2]
                    }
                    
                    result = make_api_request("/register", method="POST", data=register_data)
                    
                    if "error" not in result:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error(f"Registration failed: {result['error']}")
                else:
                    st.error("Please fill all fields")

def show_chat_page():
    """Display chat interface"""
    st.title("💬 Chat with Vakta AI")
    
    # User info sidebar
    if st.session_state.user_info:
        with st.sidebar:
            st.write(f"**Welcome, {st.session_state.user_info['full_name']}!**")
            st.write(f"Level: {st.session_state.user_info.get('current_level', 'Beginner')}")
            st.write(f"Sessions: {st.session_state.user_info.get('total_sessions', 0)}")
            
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.access_token = None
                st.session_state.user_info = None
                st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "score" in message:
                st.caption(f"Fluency Score: {message['score']:.1f}/100")

    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_chat_message(prompt)
                
                if "error" not in response:
                    ai_message = response.get("response", "No response received")
                    fluency_score = response.get("fluency_score", 0)
                    
                    st.markdown(ai_message)
                    st.caption(f"Fluency Score: {fluency_score}/100")
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": ai_message,
                        "score": fluency_score
                    })
                else:
                    error_msg = f"Error: {response['error']}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })

# Main app logic
def main():
    st.set_page_config(
        page_title="Vakta AI",
        page_icon="🗣️",
        layout="wide"
    )
    
    if st.session_state.authenticated:
        show_chat_page()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
