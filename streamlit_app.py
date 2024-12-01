import streamlit as st
import os
import requests
from datetime import datetime
from typing import Optional

# API endpoint configurations
API_BASE_URL = "http://localhost:8000"

class APIClient:
    @staticmethod
    def initialize_system(pdf_path: str) -> dict:
        """Initialize the system through the API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/initialize",
                json={"pdf_path": pdf_path}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error initializing system: {str(e)}")

    @staticmethod
    def smart_ask(question: str) -> dict:
        """Get answer from smart FastAPI endpoint"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/smart-ask",
                json={"question": question}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting answer: {str(e)}")

    @staticmethod
    def normal_ask(question: str) -> dict:
        """Get answer from normal FastAPI endpoint"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/ask",
                json={"question": question}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting answer: {str(e)}")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = None

def add_message(role: str, content: str, metadata: dict = None):
    """Add a message to chat history with metadata"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": timestamp,
        "metadata": metadata
    })

def display_chat():
    """Display the chat history with metadata"""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("metadata"):
                with st.expander("Query Details"):
                    st.json(message["metadata"])
            st.caption(f"Time: {message['timestamp']}")

def select_chat_mode():
    """Let user select chat mode"""
    st.sidebar.header("Chat Mode Selection")
    mode = st.sidebar.radio(
        "Select Chat Mode:",
        options=["Smart Chat (with query classification)", "Normal Chat (direct PDF query)"],
        index=None,
        help="Smart Chat uses AI to determine if context is needed. Normal Chat always uses PDF context."
    )
    
    if mode:
        if mode.startswith("Smart"):
            st.session_state.chat_mode = "smart"
        else:
            st.session_state.chat_mode = "normal"
        
        # Add system message about selected mode
        mode_message = (
            "Smart Chat Mode activated! I'll intelligently determine when to use the PDF context." 
            if st.session_state.chat_mode == "smart"
            else "Normal Chat Mode activated! I'll always use the PDF context for answers."
        )
        add_message("system", mode_message)


def clear_chat():
    """Clear the chat history"""
    st.session_state.chat_history = []
def main():
    st.set_page_config(page_title="PDF Chat Assistant", layout="wide")
    st.title("PDF Chat Assistant")

    # Sidebar for PDF upload and mode selection
    with st.sidebar:
        st.header("Upload PDF")
        # Add Clear Chat button at the top of sidebar
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file:
            # Save uploaded file
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            if st.button("Process PDF"):
                with st.spinner("Processing PDF..."):
                    try:
                        # Initialize system with new PDF
                        APIClient.initialize_system(temp_path)
                        st.session_state.pdf_processed = True
                        add_message("system", f"PDF '{uploaded_file.name}' processed successfully! Please select a chat mode to begin.")
                        st.success("PDF processed successfully!")
                        # Reset chat mode when new PDF is processed
                        st.session_state.chat_mode = None
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                        st.session_state.pdf_processed = False

        # Show mode selection only after PDF is processed
        if st.session_state.pdf_processed and st.session_state.chat_mode is None:
            select_chat_mode()

    # Main chat interface
    st.header("Chat")
    
    # Question input
    if st.session_state.pdf_processed and st.session_state.chat_mode:
        question = st.chat_input(
            f"Ask a question ({st.session_state.chat_mode.capitalize()} Mode)"
        )
        
        if question:
            # Add user question to chat
            add_message("user", question)

            # Get AI response based on selected mode
            with st.spinner("Getting answer..."):
                try:
                    if st.session_state.chat_mode == "smart":
                        response = APIClient.smart_ask(question)
                        add_message(
                            "assistant", 
                            response["answer"],
                            metadata={
                                "query_type": response["query_type"],
                                "confidence": response["confidence"],
                                "context_used": response["context_used"]
                            }
                        )
                    else:
                        response = APIClient.normal_ask(question)
                        add_message(
                            "assistant", 
                            response["answer"],
                            metadata={"mode": "normal_chat"}
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    elif not st.session_state.pdf_processed:
        st.info("Please upload and process a PDF first to start chatting!")
    else:
        st.info("Please select a chat mode to begin chatting!")

    # Display chat history
    display_chat()

    # Add mode switching button in sidebar
    if st.session_state.pdf_processed and st.session_state.chat_mode:
        if st.sidebar.button("Switch Chat Mode"):
            st.session_state.chat_mode = None
            st.rerun()

if __name__ == "__main__":
    main()