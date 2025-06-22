import streamlit as st
import os
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="AgroGPT - Your Agricultural Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
        color: #333333;
        font-size: 14px;
        line-height: 1.5;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: auto;
        border-left: 4px solid #2196F3;
        color: #1565C0;
    }
    .bot-message {
        background-color: #F1F8E9;
        margin-right: auto;
        border-left: 4px solid #4CAF50;
        color: #2E7D32;
    }
    .sidebar-content {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .quick-question {
        background-color: #E8F5E8;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        cursor: pointer;
        border: 1px solid #4CAF50;
        color: #2E7D32;
        font-weight: 500;
    }
    .quick-question:hover {
        background-color: #D4EDDA;
        color: #1B5E20;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "https://router.huggingface.co/fireworks-ai/inference/v1/chat/completions"

def get_headers():
    """Get API headers with token from environment or user input"""
    if 'HF_TOKEN' in os.environ:
        return {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
    elif st.session_state.get('api_token'):
        return {"Authorization": f"Bearer {st.session_state.api_token}"}
    else:
        return None

def query_ai(messages, model="accounts/fireworks/models/deepseek-r1-0528"):
    """Query the AI model with proper error handling"""
    headers = get_headers()
    if not headers:
        return {"error": "API token not provided"}
    
    payload = {
        "messages": messages,
        "model": model,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'api_token' not in st.session_state:
    st.session_state.api_token = ""

# Header
st.markdown("""
<div class="main-header">
    <h1>🌾 AgroGPT</h1>
    <p>Your AI-Powered Agricultural Assistant</p>
    <p>Get expert advice on farming, crops, seasons, and agricultural practices</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    
    # API Token input
    if 'HF_TOKEN' not in os.environ:
        st.session_state.api_token = st.text_input(
            "Enter your Hugging Face API Token:",
            type="password",
            value=st.session_state.api_token,
            help="Get your token from https://huggingface.co/settings/tokens"
        )
    else:
        st.success("✅ API Token loaded from environment")
    
    st.markdown("---")
    
    # Quick Questions
    st.header("🚀 Quick Questions")
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    quick_questions = [
        "What crops are best for monsoon season?",
        "How to identify plant diseases?",
        "Organic farming techniques for beginners",
        "Best irrigation methods for water conservation",
        "Soil testing and nutrient management",
        "Pest control without harmful chemicals",
        "Crop rotation benefits and practices",
        "Post-harvest storage techniques"
    ]
    
    for question in quick_questions:
        if st.button(question, key=f"quick_{question[:20]}"):
            st.session_state.current_question = question
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Statistics
    st.markdown("---")
    st.header("📊 Chat Statistics")
    st.metric("Total Messages", len(st.session_state.chat_history))
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    st.header("💬 Chat with AgroGPT")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong style="color: #1565C0;">👤 You:</strong><br>
                    <span style="color: #1565C0;">{message['content']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong style="color: #2E7D32;">🌾 AgroGPT:</strong><br>
                    <span style="color: #2E7D32;">{message['content']}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_area(
        "Ask your agricultural question:",
        placeholder="e.g., What are the best practices for growing tomatoes in summer?",
        height=100,
        key="user_input"
    )
    
    # Handle quick questions
    if 'current_question' in st.session_state:
        user_input = st.session_state.current_question
        del st.session_state.current_question
    
    col_send, col_example = st.columns([1, 2])
    
    with col_send:
        send_button = st.button("🚀 Send Message", type="primary")
    
    with col_example:
        if st.button("💡 Show Example Questions"):
            st.info("""
            **Example Questions:**
            - What's the best time to plant rice?
            - How can I improve soil fertility naturally?
            - What are the signs of nitrogen deficiency in plants?
            - Which crops are suitable for my climate zone?
            """)

with col2:
    st.header("📚 Agricultural Tips")
    
    tips = [
        "🌱 **Soil Health**: Test your soil pH regularly. Most crops prefer slightly acidic to neutral soil (6.0-7.0 pH).",
        "💧 **Water Management**: Water plants early morning or late evening to reduce evaporation.",
        "🐛 **Natural Pest Control**: Companion planting can help deter pests naturally.",
        "🌾 **Crop Rotation**: Rotate crops annually to prevent soil depletion and disease buildup.",
        "🌿 **Organic Matter**: Add compost to improve soil structure and fertility.",
        "📅 **Seasonal Planning**: Plan your planting schedule according to local climate patterns."
    ]
    
    for tip in tips:
        st.markdown(f"""
        <div style="background-color: #F0F8F0; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #4CAF50;">
            {tip}
        </div>
        """, unsafe_allow_html=True)

# Process user input
if send_button and user_input.strip():
    headers = get_headers()
    if not headers:
        st.error("Please provide your Hugging Face API token in the sidebar.")
    else:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Prepare messages for AI with agricultural context
        system_message = {
            "role": "system",
            "content": """You are AgroGPT, an expert agricultural assistant. You help farmers, agricultural students, and anyone interested in farming with their questions about:
            - Crop cultivation and management
            - Soil health and fertilization
            - Pest and disease control
            - Irrigation and water management
            - Seasonal farming practices
            - Organic farming techniques
            - Agricultural technology and tools
            - Post-harvest processing and storage
            
            Provide practical, accurate, and helpful advice. Always consider sustainable and environmentally friendly practices. If you're unsure about specific regional practices, ask for the user's location for more targeted advice."""
        }
        
        messages = [system_message] + [
            {"role": msg['role'], "content": msg['content']} 
            for msg in st.session_state.chat_history[-10:]  # Last 10 messages for context
        ]
        
        # Show loading spinner
        with st.spinner("🤔 AgroGPT is thinking..."):
            response = query_ai(messages)
        
        if 'error' in response:
            st.error(f"Error: {response['error']}")
        else:
            try:
                bot_response = response['choices'][0]['message']['content']
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': bot_response,
                    'timestamp': datetime.now()
                })
                st.rerun()
            except (KeyError, IndexError) as e:
                st.error(f"Unexpected response format: {e}")
                st.json(response)  # Show raw response for debugging

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🌾 AgroGPT - Empowering Agriculture with AI</p>
    <p>Built with ❤️ for farmers and agricultural enthusiasts</p>
    <p><small>Disclaimer: This is an AI assistant. Always consult with local agricultural experts for specific regional advice.</small></p>
</div>
""", unsafe_allow_html=True)