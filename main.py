from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
from utils.action_handler import ActionHandler
from utils.smart_query_router import SmartQueryRouter
from utils.pdf_processor import PDFProcessor
from store_embeddings import query_similar_chunks
import json

DEFAULT_PDF_PATH= "ncert_ch11.pdf"

class Query(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    query_type: str
    confidence: float
    context_used: bool
    tool_used: Optional[str] = None
    tool_result: Optional[dict] = None

class InitializeRequest(BaseModel):
    pdf_path: Optional[str] = DEFAULT_PDF_PATH

app = FastAPI()
client = OpenAI()
pdf_processor = PDFProcessor()

@app.post("/ask")
async def answer_question(query: Query):
    """Basic Q&A endpoint that always uses PDF context"""
    if pdf_processor.collection is None:
        raise HTTPException(
            status_code=400,
            detail="System not initialized. Please call /initialize endpoint first"
        )
    
    similar_chunks, is_relevant = query_similar_chunks(query.question, pdf_processor.collection)
    context = similar_chunks['documents'][0][0]
    
    prompt = f"""Based on the following context, answer the question.
    Context: {context}
    Question: {query.question}"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful physics teacher."},
            {"role": "user", "content": prompt}
        ]
    )

    return QueryResponse(
        answer=response.choices[0].message.content,
        query_type="basic_qa",
        confidence=1.0 if is_relevant else 0.5,
        context_used=True
    )

@app.post("/smart-ask")
async def smart_answer_question(query: Query):
    """Smart endpoint that determines whether to use PDF context or not"""
    if not hasattr(app.state, "query_router"):
        app.state.query_router = SmartQueryRouter()

    try:
        classification = await app.state.query_router.classify_query(query.question)
        
        if classification["category"] == "document_query":
            if pdf_processor.collection is None:
                raise HTTPException(
                    status_code=400,
                    detail="System not initialized. Please call /initialize endpoint first"
                )
            
            similar_chunks, is_relevant = query_similar_chunks(query.question, pdf_processor.collection)
            context = similar_chunks['documents'][0][0]
            prompt = f"""Based on the following context, answer the question.
            Context: {context}
            Question: {query.question}"""
            system_prompt = "You are a helpful physics teacher."
        else:
            prompt = query.question
            system_prompt = "You are a helpful assistant."

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

@app.post("/learning-tools")
async def learning_tools_qa(query: Query):
    """Enhanced Q&A endpoint that integrates learning tools based on query analysis"""
    if not hasattr(app.state, "action_handler"):
        app.state.action_handler = ActionHandler(pdf_processor)

    try:
        # First, check if any learning tool would be helpful
        tool_analysis = await app.state.action_handler.analyze_query_for_tools(query.question)

        print("tool analysis is ", tool_analysis)

        
        # Get relevant context if needed
        context = None
        if pdf_processor.collection is not None:
            print("going inside collection  as pdf_processor collection is not none")
            print("pdf procceor is ", pdf_processor.collection)

            similar_chunks, is_relevant = query_similar_chunks(query.question, pdf_processor.collection)
            context = similar_chunks['documents'][0][0] if similar_chunks['documents'] else None

            print("context is ", context)
        
        # if context is None:


        if tool_analysis["should_use_tool"]:
            # Execute the tool action
            tool_result = await app.state.action_handler.execute_action(
                tool_analysis["tool"],
                tool_analysis["parameters"],
                context
            )

            print("tool result is ", tool_result)
            
            # Generate a natural response that incorporates the tool result
            final_response = await app.state.action_handler.generate_tool_response(
                query.question,
                tool_result,
                tool_analysis["tool"]
            )

            print("final_response is ", final_response)
            
            
            return QueryResponse(
                answer=final_response,
                query_type="learning_tool",
                confidence=tool_analysis["confidence"],
                context_used=context is not None,
                tool_used=tool_analysis["tool"],
                tool_result=tool_result
            )
        else:
            # Fall back to regular Q&A if no tool is applicable
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful teacher."},
                    {"role": "user", "content": query.question}
                ]
            )
            
            return QueryResponse(
                answer=response.choices[0].message.content,
                query_type="regular_qa",
                confidence=1.0,
                context_used=context is not None
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/initialize")
async def initialize_system(request: InitializeRequest):
    """Initialize the QA system with a PDF file"""
    try:
        pdf_processor.process_pdf(request.pdf_path)
        return {"status": "success", "message": "System initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")