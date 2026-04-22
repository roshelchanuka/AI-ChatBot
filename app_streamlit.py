
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# ─────────────────────────────────────────
# 1. CONFIGURATION
# ─────────────────────────────────────────
load_dotenv()

# Page settings (must be the first Streamlit command)
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

SYSTEM_PROMPT = """You are a helpful, friendly, and knowledgeable AI assistant.
You give clear and concise answers. If you are unsure, you say so honestly."""

MODEL = "gpt-4o-mini"

# ─────────────────────────────────────────
# 2. INITIALIZE THE OPENAI CLIENT
# ─────────────────────────────────────────
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error(" API key not found! Please create a .env file with OPENAI_API_KEY.")
    st.stop()  # Stop rendering the rest of the app

client = OpenAI(api_key=api_key)

# ─────────────────────────────────────────
# 3. INITIALIZE SESSION STATE
# ─────────────────────────────────────────
# This runs only ONCE when the app first loads
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# ─────────────────────────────────────────
# 4. HEADER AND SIDEBAR
# ─────────────────────────────────────────
st.title(" AI Chatbot")
st.markdown("*Powered by OpenAI GPT · Built with Python & Streamlit*")

with st.sidebar:
    st.header(" Settings")
    
    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative. Lower = more factual."
    )
    
    max_tokens = st.slider(
        "Max Response Length",
        min_value=50,
        max_value=1000,
        value=500,
        step=50,
        help="Maximum number of words in AI response."
    )
    
    st.divider()
    
    # Show message count
    msg_count = len([m for m in st.session_state.messages if m["role"] != "system"])
    st.metric("Messages in history", msg_count)
    
    # Reset button
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

# ─────────────────────────────────────────
# 5. DISPLAY CHAT HISTORY
# ─────────────────────────────────────────
# Loop through all messages (skip the system message)
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────
# 6. HANDLE NEW USER INPUT
# ─────────────────────────────────────────
# st.chat_input shows a text box at the bottom of the page
if prompt := st.chat_input("Type your message here..."):
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Call the AI API and display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=st.session_state.messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                ai_reply = response.choices.message.content
                st.markdown(ai_reply)
                
                # Add AI reply to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_reply
                })
                
            except Exception as e:
                error_msg = f" Error: {str(e)}"
                st.error(error_msg)
                # Remove the failed user message
                st.session_state.messages.pop()
