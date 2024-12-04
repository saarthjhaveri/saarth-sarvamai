import streamlit as st
import os
import requests
from datetime import datetime
from typing import Optional
import json

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

def add_message(role: str, content: str, metadata: Optional[dict] = None):
    """Add a message to chat history"""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "metadata": metadata if metadata is not None else {},  # Initialize empty dict if None
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

def display_tool_result(result_type: str, data: dict):
    """Display various tool results in an organized manner"""
    try:
        if result_type == "create_flashcards":
            st.subheader("Flashcards")
            flashcards = data.get("flashcards", [])
            for i, card in enumerate(flashcards, 1):
                with st.expander(f"Flashcard {i}"):
                    st.markdown("**Question:**")
                    st.write(card["front"])
                    st.markdown("**Answer:**")
                    st.write(card["back"])

        elif result_type == "generate_practice":
            st.subheader("Practice Problems")
            problems = data.get("problems", [])
            for i, prob in enumerate(problems, 1):
                st.markdown(f"**Problem {i}**")
                st.markdown("**Question:**")
                st.write(prob["question"])
                st.markdown("**Solution:**")
                st.write(prob["solution"])
                st.markdown("**Final Answer:**")
                st.write(prob["final_answer"])
                st.markdown("**Explanation:**")
                st.write(prob["explanation"])
                st.divider()  # Add a visual separator between problems


        elif result_type == "create_concept_map":
            st.subheader("Concept Map")
            central = data.get("central_concept", "")
            connections = data.get("connections", [])
            
            st.markdown(f"**Central Concept:** {central}")
            for conn in connections:
                with st.expander(conn["concept"]):
                    st.markdown(f"**Relationship:** {conn['relationship']}")
                    st.markdown("**Sub-concepts:**")
                    for sub in conn.get("sub_concepts", []):
                        st.write(f"- {sub}")

        elif result_type == "generate_summary":
            st.subheader("Summary")
            with st.expander("Main Points"):
                for point in data.get("main_points", []):
                    st.write(f"• {point}")
            
            with st.expander("Detailed Explanations"):
                for concept, explanation in data.get("details", {}).items():
                    st.markdown(f"**{concept}:**")
                    st.write(explanation)
            
            with st.expander("Examples"):
                for example in data.get("examples", []):
                    st.write(f"- {example}")
            
            if "additional_notes" in data:
                st.markdown("**Additional Notes:**")
                st.write(data["additional_notes"])

    except Exception as e:
        st.error(f"Error displaying tool result: {str(e)}")

def display_tool_result(result_type: str, data: dict):
    """Display various tool results in an organized manner"""
    try:
        if result_type == "create_flashcards":
            st.subheader("Flashcards")
            flashcards = data.get("flashcards", [])
            
            # Create columns for navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            
            # Initialize flashcard index in session state if not exists
            if 'flashcard_index' not in st.session_state:
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
            
            # Navigation buttons
            with col1:
                if st.button("Previous") and st.session_state.flashcard_index > 0:
                    st.session_state.flashcard_index -= 1
                    st.session_state.show_answer = False
            
            with col3:
                if st.button("Next") and st.session_state.flashcard_index < len(flashcards) - 1:
                    st.session_state.flashcard_index += 1
                    st.session_state.show_answer = False
            
            # Display current flashcard
            current_card = flashcards[st.session_state.flashcard_index]
            with st.container():
                st.markdown(f"**Card {st.session_state.flashcard_index + 1} of {len(flashcards)}**")
                st.markdown("**Question:**")
                st.write(current_card["front"])
                
                if st.button("Reveal Answer"):
                    st.session_state.show_answer = not st.session_state.show_answer
                
                if st.session_state.show_answer:
                    st.markdown("**Answer:**")
                    st.write(current_card["back"])

        elif result_type == "generate_practice":
            st.subheader("Practice Problems")
            problems = data.get("problems", [])
            
            # Initialize problem state if not exists
            if 'problem_states' not in st.session_state:
                st.session_state.problem_states = [{
                    'show_solution': False,
                    'show_answer': False,
                    'show_explanation': False
                } for _ in problems]
            
            for i, prob in enumerate(problems):
                with st.expander(f"Problem {i + 1}: {prob['question'][:50]}...", expanded=(i == 0)):
                    st.markdown("**Question:**")
                    st.write(prob["question"])
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"Solution #{i+1}", key=f"sol_{i}"):
                            st.session_state.problem_states[i]['show_solution'] = not st.session_state.problem_states[i]['show_solution']
                    with col2:
                        if st.button(f"Answer #{i+1}", key=f"ans_{i}"):
                            st.session_state.problem_states[i]['show_answer'] = not st.session_state.problem_states[i]['show_answer']
                    with col3:
                        if st.button(f"Explanation #{i+1}", key=f"exp_{i}"):
                            st.session_state.problem_states[i]['show_explanation'] = not st.session_state.problem_states[i]['show_explanation']
                    
                    if st.session_state.problem_states[i]['show_solution']:
                        st.markdown("**Solution:**")
                        st.write(prob["solution"])
                    
                    if st.session_state.problem_states[i]['show_answer']:
                        st.markdown("**Final Answer:**")
                        st.write(prob["final_answer"])
                    
                    if st.session_state.problem_states[i]['show_explanation']:
                        st.markdown("**Explanation:**")
                        st.write(prob["explanation"])

        elif result_type == "create_concept_map":
            st.subheader("Concept Map")
            central = data.get("central_concept", "")
            connections = data.get("connections", [])
            
            # Display central concept in a prominent way
            st.markdown(f"### Central Concept: {central}")
            st.divider()
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["Hierarchical View", "Detailed View"])
            
            with tab1:
                # Display hierarchical structure
                for i, conn in enumerate(connections):
                    st.markdown(f"**{i+1}. {conn['concept']}**")
                    st.markdown(f"↳ *Relationship:* {conn['relationship']}")
                    for sub in conn.get("sub_concepts", []):
                        st.markdown(f"  • {sub}")
            
            with tab2:
                # Display detailed expandable view
                for conn in connections:
                    with st.expander(conn["concept"]):
                        st.markdown(f"**Relationship to Central Concept:**")
                        st.write(conn['relationship'])
                        st.markdown("**Sub-concepts:**")
                        for sub in conn.get("sub_concepts", []):
                            st.write(f"- {sub}")

        elif result_type == "generate_summary":
            st.subheader("Summary")
            
            # Create tabs for different sections of the summary
            tabs = st.tabs(["Main Points", "Details", "Examples", "Additional Notes"])
            
            with tabs[0]:
                st.markdown("### Key Points")
                for point in data.get("main_points", []):
                    st.write(f"• {point}")
            
            with tabs[1]:
                st.markdown("### Detailed Explanations")
                for concept, explanation in data.get("details", {}).items():
                    with st.expander(concept):
                        st.write(explanation)
            
            with tabs[2]:
                st.markdown("### Examples")
                for i, example in enumerate(data.get("examples", []), 1):
                    st.markdown(f"**Example {i}:**")
                    st.write(example)
            
            with tabs[3]:
                if "additional_notes" in data:
                    st.markdown("### Additional Notes")
                    st.write(data["additional_notes"])

    except Exception as e:
        st.error(f"Error displaying tool result: {str(e)}")


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
    if st.session_state.pdf_processed:
        question = st.chat_input("Type your question here...")
        
        if question:
            add_message("user", question)
            
            with st.spinner("Processing..."):
                try:
                    if st.session_state.current_mode == "Basic Q&A":
                        response = APIClient.ask(question)
                        add_message(
                            "assistant",
                            response["answer"],
                            metadata={
                                "query_type": "basic_qa",
                                "context_used": True
                            }
                        )
                    elif st.session_state.current_mode == "Smart Q&A":
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
                    else:  # Learning Tools
                        response = APIClient.learning_tools_qa(question)
                        add_message(
                            "assistant",
                            response["answer"],
                            metadata={
                                "query_type": response["query_type"],
                                "confidence": response["confidence"],
                                "context_used": response["context_used"],
                                "tool_used": response.get("tool_used"),
                                "tool_result": response.get("tool_result")
                            }
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Please upload and process a PDF to start.")

if __name__ == "__main__":
    main()