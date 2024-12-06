# saarth-sarvamai
This repo includes the assignment task for sarvam ai engineering role  https://docs.google.com/document/d/1y6Ol_9cLP1VPrHUR7NfXcYtAECZRXAhmmTKM5sc24HQ/edit?tab=t.0


# Saarth-Sarvamai

This repository contains the assignment task for the Sarvam AI engineering role.

## Project Structure

    .
    ├── sarvamai_tools/          # Tools for STT, TTS, and translation
    ├── utils/                   # Utility functions and core logic
    │   ├── embeddings/         # Embedding generation and storage
    │   └── filter/            # PDF text extraction and cleaning
    ├── streamlit_app.py        # Frontend Streamlit application
    ├── main.py                # Backend FastAPI server
    └── requirements.txt       # Project dependencies

## Setup Instructions

### 1. Create and Activate Virtual Environment

For Windows:

    python -m venv venv
    .\venv\Scripts\activate

For Linux/Mac:

    python3 -m venv venv
    source venv/bin/activate

### 2. Install Dependencies

    pip install -r requirements.txt

### 3. Environment Variables

Create a .env file in the root directory with the following variables:

    OPENAI_API_KEY=your_openai_api_key
    SARVAM_API_KEY=your_sarvam_api_key

### 4. Running the Application

Start the FastAPI backend server:

    uvicorn main:app --reload --port 8000

Start the Streamlit frontend application (in a new terminal):

    streamlit run streamlit_app.py

The application should now be running at:
- Backend: http://localhost:8000
- Frontend: http://localhost:8501

## Features

1. PDF Processing
   - Upload and process PDF documents
   - Extract text and generate embeddings
   - Store in vector database for efficient retrieval

2. Question Answering
   - Basic Q&A: Direct answers from document context
   - Smart Q&A: Intelligent routing based on query type
   - Learning Tools: Interactive educational features

3. Learning Tools
   - Flashcards
   - Practice Problems
   - Concept Maps
   - Interactive Summaries

4. Voice Interaction
   - Speech-to-Text input
   - Text-to-Speech output
   - Multi-language support

## API Endpoints

1. /initialize
   - POST request
   - Initializes system with PDF document

2. /ask
   - POST request
   - Basic question answering

3. /smart-ask
   - POST request
   - Smart query routing and answering

4. /learning-tools
   - POST request
   - Educational tool generation

## Usage Instructions

1. Start both the backend and frontend servers
2. Upload a PDF document through the Streamlit interface
3. Click "Process PDF" to initialize the system
4. Select interaction mode (Basic Q&A, Smart Q&A, or Learning Tools)
5. Enter questions or requests in the chat interface
6. Use voice input option for speech interaction

## Technical Requirements

- Python 3.8 or higher
- OpenAI API access
- Sarvam AI API access
- Sufficient storage for vector database
- Internet connection for API calls

## Error Handling

The application includes comprehensive error handling for:
- PDF processing issues
- API connection failures
- Invalid user inputs
- Server communication errors

## Performance Considerations

- PDF size limitations
- API rate limiting
- Memory usage for embeddings
- Response time optimization

## License

This project is proprietary and confidential.
