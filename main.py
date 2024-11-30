from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
from utils.smart_query_router import SmartQueryRouter
from utils.pdf_processor import PDFProcessor
from store_embeddings import query_similar_chunks


DEFAULT_PDF_PATH = "ncert_ch11.pdf"

class Query(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    query_type: str
    confidence: float
    context_used: bool

class InitializeRequest(BaseModel):
    pdf_path: Optional[str] = DEFAULT_PDF_PATH

app = FastAPI()
client = OpenAI()
pdf_processor = PDFProcessor()
query_router = SmartQueryRouter()


@app.post("/smart-ask", response_model=QueryResponse)
async def smart_answer_question(query: Query):
    """Smart endpoint that determines whether to use PDF context or not"""
    if not hasattr(app.state, "query_router"):
        app.state.query_router = SmartQueryRouter()

    try:
        # Classify the query
        classification = await app.state.query_router.classify_query(query.question)
        
        if classification["category"] == "document_query":
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
            
            system_prompt = "You are a helpful physics teacher."
            
        else:
            # Handle non-document queries
            prompt = query.question
            system_prompt = """You are a helpful assistant. For system-related questions, 
            explain about the PDF chat system. For general conversation, be friendly and engaging."""

        # Get response from LLM
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        return QueryResponse(
            answer=response.choices[0].message.content,
            query_type=classification["category"],
            confidence=classification["confidence"],
            context_used=classification["requires_context"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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