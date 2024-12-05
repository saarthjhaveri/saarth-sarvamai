import base64
import streamlit as st
import os
import requests
from datetime import datetime
from typing import Optional
import json
import tempfile
from audio_recorder_streamlit import audio_recorder
from sarvamai_tools.stt_check import transcribe_and_translate_audio
from sarvamai_tools.tts_check import text_to_speech


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
    def ask(question: str) -> dict:
        """Get answer from basic FastAPI endpoint"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/ask",
                json={"question": question}
            )
            response.raise_for_status()
            print("response json for the query is ", response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting answer: {str(e)}")

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
    def learning_tools_qa(question: str) -> dict:
        """Get answer from learning tools endpoint"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/learning-tools",
                json={"question": question}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting answer: {str(e)}")

def init_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "smart_qa"

def add_message(role: str, content: str, metadata: Optional[dict] = None, audio_data: Optional[bytes] = None):
    """Add a message to chat history"""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "metadata": metadata if metadata is not None else {},
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "audio_data": audio_data if audio_data else None
    })

def display_tool_result(result_type: str, data: dict):
    """Display various tool results in an organized manner"""
    try:
        if result_type == "create_flashcards":
            st.subheader("Flashcards")
            flashcards = data.get("flashcards", [])
            
            # Custom CSS for flashcard styling
            st.markdown("""
                <style>
                    .flashcard {
                        padding: 20px;
                        border-radius: 10px;
                        margin: 10px 0;
                        min-height: 200px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        text-align: center;
                        font-size: 1.2em;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        transition: transform 0.3s ease;
                    }
                    .question-card {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .answer-card {
                        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
                        color: #1a1a1a;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Initialize session state
            if 'flashcard_index' not in st.session_state:
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
            
            # Create three columns for navigation and card display
            left_col, center_col, right_col = st.columns([1, 3, 1])
            
            with center_col:
                # Display progress
                progress_text = f"Card {st.session_state.flashcard_index + 1} of {len(flashcards)}"
                st.progress((st.session_state.flashcard_index + 1) / len(flashcards))
                st.markdown(f"<p style='text-align: center'>{progress_text}</p>", unsafe_allow_html=True)
                
                # Display current card
                current_card = flashcards[st.session_state.flashcard_index]
                
                if not st.session_state.show_answer:
                    st.markdown(f"""
                        <div class="flashcard question-card">
                            {current_card["front"]}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="flashcard answer-card">
                            {current_card["back"]}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Navigation controls
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                if st.button("← Previous", key="prev") and st.session_state.flashcard_index > 0:
                    st.session_state.flashcard_index -= 1
                    st.session_state.show_answer = False
                    st.rerun()
            
            with col2:
                if st.button("Flip Card", key="flip"):
                    st.session_state.show_answer = not st.session_state.show_answer
                    st.rerun()
            
            with col3:
                if st.button("Next →", key="next") and st.session_state.flashcard_index < len(flashcards) - 1:
                    st.session_state.flashcard_index += 1
                    st.session_state.show_answer = False
                    st.rerun()
            
            with col4:
                if st.button("Shuffle", key="shuffle"):
                    import random
                    st.session_state.flashcard_index = random.randint(0, len(flashcards) - 1)
                    st.session_state.show_answer = False
                    st.rerun()

      
        elif result_type == "generate_practice":
            st.subheader("Practice Problems")
            problems = data.get("problems", [])
            
            # Custom CSS for practice problems
            st.markdown("""
                <style>
                    .problem-card {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                        border-radius: 15px;
                        color: white;
                        margin: 20px 0;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                    }
                    .solution-section {
                        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin: 10px 0;
                        color: #1a1a1a;
                    }
                    .answer-section {
                        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin: 10px 0;
                        color: #1a1a1a;
                    }
                    .explanation-section {
                        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin: 10px 0;
                        color: #1a1a1a;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Initialize session state for problem visibility
            if 'problem_states' not in st.session_state:
                st.session_state.problem_states = [{
                    'show_solution': False,
                    'show_answer': False,
                    'show_explanation': False
                } for _ in problems]
            
            # Display problems
            for i, prob in enumerate(problems):
                st.markdown(f"""
                    <div class="problem-card">
                        <h3>Problem {i + 1}</h3>
                        <p>{prob["question"]}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Solution {i + 1}", key=f"sol_btn_{i}"):
                        st.session_state.problem_states[i]['show_solution'] = not st.session_state.problem_states[i]['show_solution']
                
                with col2:
                    if st.button(f"Final Answer {i + 1}", key=f"ans_btn_{i}"):
                        st.session_state.problem_states[i]['show_answer'] = not st.session_state.problem_states[i]['show_answer']
                
                with col3:
                    if st.button(f"Explanation {i + 1}", key=f"exp_btn_{i}"):
                        st.session_state.problem_states[i]['show_explanation'] = not st.session_state.problem_states[i]['show_explanation']
                
                # Show/Hide sections based on button states
                if st.session_state.problem_states[i]['show_solution']:
                    st.markdown(f"""
                        <div class="solution-section">
                            <strong>Step-by-step Solution:</strong><br>
                            {prob["solution"]}
                        </div>
                    """, unsafe_allow_html=True)
                
                if st.session_state.problem_states[i]['show_answer']:
                    st.markdown(f"""
                        <div class="answer-section">
                            <strong>Final Answer:</strong><br>
                            {prob["final_answer"]}
                        </div>
                    """, unsafe_allow_html=True)
                
                if st.session_state.problem_states[i]['show_explanation']:
                    st.markdown(f"""
                        <div class="explanation-section">
                            <strong>Explanation:</strong><br>
                            {prob["explanation"]}
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
        elif result_type == "create_concept_map":
            st.subheader("Interactive Concept Map")
            central = data.get("central_concept", "")
            connections = data.get("connections", [])
            
            # Enhanced Custom CSS for concept map
            st.markdown("""
                <style>
                    /* Central Concept Styling */
                    .concept-central {
                        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                        padding: 20px;
                        border-radius: 15px;
                        color: white;
                        text-align: center;
                        margin: 20px auto;
                        max-width: 80%;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        transition: all 0.3s ease;
                    }
                    .concept-central:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.3);
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Display central concept
            st.markdown(f"""
                <div class="concept-central">
                    <h2>{central}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Only show the Detailed View
            for conn in connections:
                with st.expander(conn["concept"]):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown("**Relationship:**")
                        st.info(conn['relationship'])
                    with col2:
                        st.markdown("**Sub-concepts:**")
                        for sub in conn.get("sub_concepts", []):
                            st.success(f"• {sub}")
        elif result_type == "generate_summary":
            st.subheader("Interactive Summary")
            
            # Custom CSS for summary sections
            st.markdown("""
                <style>
                    .summary-header {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 15px;
                        border-radius: 15px;
                        color: white;
                        margin: 20px 0 10px 0;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        text-align: center;
                    }
                    .main-point-card {
                        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin: 10px 0;
                        color: #1a1a1a;
                        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s ease;
                    }
                    .main-point-card:hover {
                        transform: translateX(10px);
                    }
                    .detail-card {
                        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin: 10px 0;
                        color: #1a1a1a;
                        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
                    }
                    .example-card {
                        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin: 10px 0;
                        color: #1a1a1a;
                        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s ease;
                    }
                    .example-card:hover {
                        transform: scale(1.02);
                    }
                    .notes-card {
                        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin: 10px 0;
                        color: white;
                        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Create tabs with fancy headers
            tab1, tab2, tab3, tab4 = st.tabs([
                "Main Points", 
                "Detailed Explanations", 
                "Examples",
                "Additional Notes"
            ])
            
            with tab1:
                st.markdown("""
                    <div class="summary-header">
                        <h3>Key Points</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                for i, point in enumerate(data.get("main_points", []), 1):
                    st.markdown(f"""
                        <div class="main-point-card">
                            <strong>{i}.</strong> {point}
                        </div>
                    """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("""
                    <div class="summary-header">
                        <h3>Detailed Explanations</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                for concept, explanation in data.get("details", {}).items():
                    with st.expander(f"**{concept}**"):
                        st.markdown(f"""
                            <div class="detail-card">
                                {explanation}
                            </div>
                        """, unsafe_allow_html=True)
            
            with tab3:
                st.markdown("""
                    <div class="summary-header">
                        <h3>Examples</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                for i, example in enumerate(data.get("examples", []), 1):
                    st.markdown(f"""
                        <div class="example-card">
                            <strong>Example {i}:</strong><br>
                            {example}
                        </div>
                    """, unsafe_allow_html=True)
            
            with tab4:
                if "additional_notes" in data:
                    st.markdown("""
                        <div class="summary-header">
                            <h3>Additional Notes</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class="notes-card">
                            {data["additional_notes"]}
                        </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying tool result: {str(e)}")


def display_chat():
    """Display chat history with proper formatting"""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            # Display regular message content
            st.write(message["content"])

            # Display audio if available
            if message.get("audio_data") is not None:
                try:
                    st.audio(message["audio_data"], format="audio/wav")
                except Exception as e:
                    st.error(f"Error playing audio: {str(e)}")
            
            # Safely handle metadata
            metadata = message.get("metadata", {})
            if metadata is not None and metadata:
                with st.expander("Response Details"):
                    st.json(metadata)
            
            # Display timestamp if present
            if "timestamp" in message:
                st.caption(f"Time: {message['timestamp']}")



def process_user_input(input_text: str, input_type: str = "text", language_code: str = "en-IN"):
    """Process user input and get response"""
    print("inside processing user input ", input_text)

    add_message("user", input_text)
    
    with st.spinner("Processing..."):
        try:
            response = APIClient.ask(input_text)
            
            # Convert response to audio if input was voice
            audio_data = None
            if input_type == "voice":
                try:
                    response_text = response["answer"][:500]
                    audio_base64 = text_to_speech(
                        text=response_text,
                        target_language=language_code,
                        speaker="meera"
                    )
                    if audio_base64:
                        audio_data = base64.b64decode(audio_base64)
                except Exception as e:
                    st.warning(f"Could not generate audio response: {str(e)}")
            
            # Store the message in session state
            add_message(
                "assistant",
                response["answer"],
                metadata={
                    "query_type": "basic_qa",
                    "confidence": response.get("confidence", 1.0),
                    "context_used": response.get("context_used", True)
                },
                audio_data=audio_data
            )
            
            # Display the latest message immediately
            with st.chat_message("assistant"):
                st.write(response["answer"])
                if audio_data:
                    st.audio(audio_data, format="audio/wav")
                
            # Force refresh to update the full chat history
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

def display_chat():
    """Display chat history with proper formatting"""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            # Display regular message content
            st.write(message["content"])

            # Display audio if available
            if message.get("audio_data") is not None:
                try:
                    st.audio(message["audio_data"], format="audio/wav")
                except Exception as e:
                    st.error(f"Error playing audio: {str(e)}")
            
            # Safely handle metadata
            metadata = message.get("metadata", {})
            if metadata is not None and metadata:
                with st.expander("Response Details"):
                    st.json(metadata)
            
            # Display timestamp if present
            if "timestamp" in message:
                st.caption(f"Time: {message['timestamp']}")

def main():
    st.set_page_config(page_title="PDF Learning Assistant", layout="wide")
    st.title("PDF Learning Assistant")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar for PDF upload and mode selection
    with st.sidebar:
        st.header("Settings")
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        # PDF upload
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        if uploaded_file:
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            if st.button("Process PDF"):
                with st.spinner("Processing PDF..."):
                    try:
                        APIClient.initialize_system(temp_path)
                        st.session_state.pdf_processed = True
                        add_message(
                            "system",
                            "PDF processed successfully! You can:\n"
                            "1. Ask questions about the content\n"
                            "2. Request explanations or summaries\n"
                            "3. Get learning materials like flashcards or practice problems\n\n"
                            "Examples:\n"
                            "- 'What are the key points about X?'\n"
                            "- 'Create flashcards for Y concept'\n"
                            "- 'Generate practice problems about Z'"
                        )
                        st.success("PDF processed successfully!")
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
        
        # Mode selection
        st.session_state.current_mode = st.radio(
            "Select Mode:",
            ["Basic Q&A", "Smart Q&A", "Learning Tools"],
            index=1  # Default to Smart Q&A
        )

    # Main chat interface
    st.header("Chat")
    display_chat()
    
    # Input area
     # Input area
        # Input area
    if st.session_state.pdf_processed:
        if st.session_state.current_mode == "Basic Q&A":
            # Create two columns with different widths
            text_col, audio_col = st.columns([0.8, 0.2])
            
            with text_col:
                question = st.chat_input("Type your question here...")
                
            with audio_col:
                # Add audio recorder in a container to align it properly
                with st.container():
                    st.write("") # Add some spacing
                    audio_bytes = audio_recorder(
                        text="",
                        recording_color="#e74c3c",
                        neutral_color="#3498db",
                        icon_size="2x"
                    )

            # Track last processed audio in session state
            if 'last_processed_audio' not in st.session_state:
                st.session_state.last_processed_audio = None
            
            
            if question:
                process_user_input(question, "text")
                
            if audio_bytes and audio_bytes != st.session_state.last_processed_audio:
                st.session_state.last_processed_audio = audio_bytes
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name
                
                try:
                    with st.spinner("Transcribing audio..."):
                        transcribed_text, language_code = transcribe_and_translate_audio(
                            audio_file_path=tmp_path,
                            prompt="This is a question about physics concepts"
                        )

                        if transcribed_text:
                            st.info(f"Transcribed: {transcribed_text}")
                            process_user_input(transcribed_text, "voice", language_code)
                        else:
                            st.error("Could not transcribe audio. Please try again.")
                            
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
        else:
            # For other modes, only show text input
            question = st.chat_input("Type your question here...")
            if question:
                process_user_input(question, "text")

if __name__ == "__main__":
    main()