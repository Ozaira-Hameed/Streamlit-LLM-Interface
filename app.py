import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Local LLM Chat Interface",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # Change this to your installed model

def query_ollama(prompt, model=MODEL_NAME):
    """Send query to Ollama and get response"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure Ollama is running (run 'ollama serve' in terminal)"
    except Exception as e:
        return f"Error: {str(e)}"

def reset_conversation():
    """Reset the conversation history"""
    st.session_state.messages = []
    st.rerun()

# Main UI
st.title("🤖 Local LLM Chat Interface")
st.markdown("*Powered by Ollama*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model selection
    available_models = ["llama3.2", "llama3", "mistral", "codellama", "deepseek-r1"]
    selected_model = st.selectbox("Select Model", available_models, index=0)
    MODEL_NAME = selected_model
    
    st.markdown("---")
    
    # Instructions
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. Make sure Ollama is running
    2. Enter your query below
    3. View responses in chat
    4. Use Reset to clear history
    """)
    
    st.markdown("---")
    
    # Conversation stats
    st.markdown("### 📊 Stats")
    st.metric("Messages", len(st.session_state.messages))
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Reset Conversation", use_container_width=True):
        reset_conversation()

# Main chat area
st.markdown("### 💬 Conversation")

# Display conversation history
chat_container = st.container()
with chat_container:
    for idx, message in enumerate(st.session_state.messages):
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant"):
                st.markdown(message['content'])

# Input area
st.markdown("---")
col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_area(
        "Your message:",
        height=100,
        placeholder="Type your question here...",
        key="user_input"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_button = st.button("Send 📤", use_container_width=True)

# Process user input
if send_button and user_input.strip():
    # Add user message to history
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })
    
    # Show spinner while processing
    with st.spinner("🤔 Thinking..."):
        # Get response from Ollama
        response = query_ollama(user_input, MODEL_NAME)
        
        # Add assistant response to history
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
    
    # Rerun to update chat display
    st.rerun()

# Export conversation button
if len(st.session_state.messages) > 0:
    st.markdown("---")
    if st.button("📥 Export Conversation"):
        conversation_text = "\n\n".join([
            f"[{msg['timestamp']}] {msg['role'].upper()}: {msg['content']}"
            for msg in st.session_state.messages
        ])
        st.download_button(
            label="Download as TXT",
            data=conversation_text,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Built with Streamlit & Ollama</p>",
    unsafe_allow_html=True
)