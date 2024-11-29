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
    def get_answer(question: str) -> str:
        """Get answer from FastAPI endpoint"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/ask",
                json={"question": question}
            )
            response.raise_for_status()
            return response.json()["answer"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting answer: {str(e)}")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False

def add_message(role: str, content: str):
    """Add a message to chat history"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

def display_chat():
    """Display the chat history"""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(f"{message['content']}")
            st.caption(f"Time: {message['timestamp']}")



def main():
    st.set_page_config(page_title="PDF Chat Assistant", layout="wide")
    st.title("PDF Chat Assistant")

    # Sidebar for PDF upload
    with st.sidebar:
        st.header("Upload PDF")
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
                        add_message("system", f"PDF '{uploaded_file.name}' processed successfully! You can now ask questions.")
                        st.success("PDF processed successfully!")
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                        st.session_state.pdf_processed = False

    # Main chat interface
    st.header("Chat")
    
    # Question input
    if st.session_state.pdf_processed:
        question = st.chat_input("Ask a question about the PDF")
        
        if question:
            # Add user question to chat
            add_message("user", question)

            # Get AI response
            with st.spinner("Getting answer..."):
                try:
                    answer = APIClient.get_answer(question)
                    add_message("assistant", answer)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Please upload and process a PDF first to start chatting!")

    # Display chat history once at the end
    display_chat()

# ... existing code ...



if __name__ == "__main__":
    main()