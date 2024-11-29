from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

from utils.pdf_processor import PDFProcessor
from store_embeddings import query_similar_chunks

# Initialize OpenAI client
client = OpenAI()

# Initialize FastAPI app
app = FastAPI()

# Global variables
pdf_processor = PDFProcessor()
DEFAULT_PDF_PATH = "ncert_ch11.pdf"

class Query(BaseModel):
    question: str

class InitializeRequest(BaseModel):
    pdf_path: Optional[str] = DEFAULT_PDF_PATH

@app.post("/initialize")
async def initialize_system(request: InitializeRequest):
    """Initialize the QA system with a PDF file"""
    try:
        # Process PDF and initialize ChromaDB
        pdf_processor.process_pdf(request.pdf_path)
        return {"status": "success", "message": "System initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@app.post("/ask")
async def answer_question(query: Query):
    """Answer questions based on the PDF content"""
    if pdf_processor.collection is None:
        raise HTTPException(
            status_code=400, 
            detail="System not initialized. Please call /initialize endpoint first"
        )
    
    # Get relevant chunks from ChromaDB
    similar_chunks = query_similar_chunks(query.question, pdf_processor.collection)
    
    # Create a prompt with the context
    prompt = f"""Based on the following context, answer the question.
    
    Context:
    {similar_chunks['documents'][0]}
    
    Question: {query.question}
    
    Answer:"""
    
    # Get response from LLM
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful physics teacher."},
            {"role": "user", "content": prompt}
        ]
    )

    print("response recieved is ", response)
    print('\n\n\n')


    
    return {"answer": response.choices[0].message.content}

@app.get("/status")
async def get_status():
    """Check if the system is initialized"""
    return {
        "initialized": pdf_processor.collection is not None,
        "current_pdf": pdf_processor.current_pdf_path if pdf_processor.collection else None
    }