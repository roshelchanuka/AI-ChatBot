import streamlit as st
import sqlite3
import os
import re
import streamlit.components.v1 as components
from database import get_user, create_user, verify_user, save_chat_message, get_chat_history, clear_chat_history
from inference_engine import get_bot_response
from emotion_detector import detect_emotion

# ─────────────────────────────────────────
# 1. CONFIGURATION & STYLES
# ─────────────────────────────────────────
st.set_page_config(page_title="TravelBot AI", layout="wide")

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 2. SESSION STATE & AUTH LOGIC
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "show_auth" not in st.session_state:
    st.session_state.show_auth = False

def render_auth_page():
    st.html("""
        <div style="text-align: center; padding: 2rem;">
            <h1 style="color: #151717; font-size: 3rem; margin-bottom: 0.5rem;">TravelBot AI</h1>
            <p style="color: #64748b; font-size: 1.2rem;">Your intelligent AI travel companion</p>
        </div>
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("### Welcome Back")
            email = st.text_input("Email", key="login_email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            
            if st.button("Sign In", key="login_btn", use_container_width=True):
                if email and password:
                    user = get_user(email)
                    if user and user[2] == password:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.messages = get_chat_history(email)
                        st.session_state.show_auth = False
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                else:
                    st.warning("Please fill in all fields.")

        with tab2:
            st.markdown("### Create Account")
            new_email = st.text_input("Email", key="signup_email", placeholder="Choose an email")
            new_password = st.text_input("Password", type="password", key="signup_pass", placeholder="Create a password")
            
            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                if new_email and new_password:
                    if get_user(new_email):
                        st.error("Email already exists.")
                    elif create_user(new_email, new_password):
                        verify_user(new_email)
                        st.session_state.authenticated = True
                        st.session_state.user_email = new_email
                        st.session_state.messages = [] # New user, empty history
                        st.session_state.show_auth = False
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Registration failed. Please try again.")
                else:
                    st.warning("Please fill in all fields.")

# ─────────────────────────────────────────
# 4. NAVIGATION & HEADER
# ─────────────────────────────────────────
def render_header():
    st.markdown(f"### 🌍 Welcome back, {st.session_state.user_email.split('@')[0]}!" if st.session_state.authenticated else "### 🌍 TravelBot Guest Session")

# --- Main Application Flow ---
if st.session_state.authenticated:
    st.session_state.show_auth = False

if st.session_state.show_auth and not st.session_state.authenticated:
    if st.button("← Back to Chat"):
        st.session_state.show_auth = False
        st.rerun()
    render_auth_page()
    st.stop()

render_header()

# ─────────────────────────────────────────
# 5. SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.title("TravelBot")
    st.divider()
    
    if st.session_state.authenticated:
        st.markdown(f"👤 **{st.session_state.user_email}**")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()
    else:
        st.markdown("👤 **Guest User**")
        if st.button("Login to Sync History"):
            st.session_state.show_auth = True
            st.rerun()
    
    st.divider()
    st.markdown("### 🛠 Tools")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        if st.session_state.authenticated:
            clear_chat_history(st.session_state.user_email)
        st.rerun()

# ─────────────────────────────────────────
# 6. CHAT INTERFACE
# ─────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your next adventure..."):
    # Detect Emotion
    emoji, emotion, color = detect_emotion(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    if st.session_state.authenticated:
        save_chat_message(st.session_state.user_email, "user", prompt)

    with st.chat_message("user"):
        st.markdown(f"{prompt} *({emotion} {emoji})*")
    
    with st.chat_message("assistant"):
        # Get actual bot response
        response, source = get_bot_response(prompt)
        
        st.markdown(response)
        st.caption(f"Source: {source}")
        st.session_state.messages.append({"role": "assistant", "content": response})
        if st.session_state.authenticated:
            save_chat_message(st.session_state.user_email, "assistant", response)
