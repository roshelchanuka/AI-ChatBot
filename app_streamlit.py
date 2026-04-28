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
    st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <h1 class="auth-title">TravelBot AI</h1>
                <p style="color: #94a3b8;">Your intelligent AI travel companion</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
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
    bubble_class = "user-bubble" if message["role"] == "user" else "bot-bubble"
    st.markdown(f'<div class="{bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask about your next adventure..."):
    # Detect Emotion
    emoji, emotion, color = detect_emotion(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    if st.session_state.authenticated:
        save_chat_message(st.session_state.user_email, "user", prompt)

    # Re-render to show new message immediately with animation
    st.rerun()

# ─────────────────────────────────────────
# 7. BOT RESPONSE HANDLING
# ─────────────────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    
    with st.spinner("TravelBot is thinking..."):
        # Get actual bot response
        response, source = get_bot_response(last_prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        if st.session_state.authenticated:
            save_chat_message(st.session_state.user_email, "assistant", response)
            # Automatic Learning: Save useful AI/Search responses to the learned_responses table
            from database import save_learned_response
            # Save if the response came from AI or Web Search (not from the local DB/Static KB)
            if len(last_prompt) > 5 and source in ["AI GPT", "Web Search", "Live Web Search"]:
                save_learned_response(last_prompt, response)
        st.rerun()

# ─────────────────────────────────────────
# 8. ASSET INJECTION (BOTTOM)
# ─────────────────────────────────────────
with open("static/style.css") as f:
    st.markdown('<style>' + f.read() + '</style>', unsafe_allow_html=True)
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

with open("static/main.js") as f:
    # Use components.html for robust JS execution that can escape to parent
    components.html(f'<script>{f.read()}</script>', height=0)
