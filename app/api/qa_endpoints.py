# app/api/qa_endpoints.py
"""
Q&A API endpoints
FIXED: Proper error handling and environment loading
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Force load environment variables
from dotenv import load_dotenv
import os
load_dotenv()

# Verify API key is loaded
api_key_preview = os.getenv('OPENAI_API_KEY', 'NOT_FOUND')
print(f"🔑 QA Endpoints: API Key = {api_key_preview[:15]}..." if len(api_key_preview) > 15 else "❌ No API Key")

from app.services.document_qa import DocumentQA

router = APIRouter(prefix="/api/v1/qa", tags=["question-answering"])

# Store Q&A sessions (in production, use Redis or database)
qa_sessions: Dict[str, DocumentQA] = {}

class QuestionRequest(BaseModel):
    session_id: str
    question: str

class QASessionCreate(BaseModel):
    session_id: str
    document_text: str
    entities: Optional[Dict[str, Any]] = None

class MultipleQuestionsRequest(BaseModel):
    session_id: str
    questions: List[str]

@router.post("/create-session")
async def create_qa_session(request: QASessionCreate):
    """
    Create a new Q&A session with document context
    """
    try:
        # Check if OpenAI API key exists
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'message': 'Q&A requires a valid OpenAI API key in .env file'
            }

        qa = DocumentQA()

        # Check if QA initialized successfully
        if not qa.client:
            return {
                'success': False,
                'error': 'Q&A initialization failed',
                'message': 'OpenAI client failed to initialize. Check API key.'
            }

        qa.set_context(request.document_text, request.entities)
        qa_sessions[request.session_id] = qa

        # Get suggested questions
        suggestions = qa.get_suggested_questions()

        return {
            'success': True,
            'session_id': request.session_id,
            'message': 'Q&A session created successfully',
            'suggested_questions': suggestions
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Q&A Session Creation Error:\n{error_details}")

        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to create Q&A session'
        }

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the document
    """
    if request.session_id not in qa_sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please create a session first.")

    qa = qa_sessions[request.session_id]
    result = qa.ask_question(request.question)

    return result

@router.post("/ask-multiple")
async def ask_multiple_questions(request: MultipleQuestionsRequest):
    """
    Ask multiple questions at once
    """
    if request.session_id not in qa_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    qa = qa_sessions[request.session_id]
    results = qa.ask_multiple(request.questions)

    return {
        'success': True,
        'answers': results
    }

@router.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Get conversation history for a session
    """
    if session_id not in qa_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    qa = qa_sessions[session_id]
    history = qa.get_conversation_history()

    return {
        'success': True,
        'session_id': session_id,
        'history': history
    }

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a Q&A session
    """
    if session_id in qa_sessions:
        del qa_sessions[session_id]
        return {'success': True, 'message': 'Session deleted'}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/suggestions/{session_id}")
async def get_suggested_questions(session_id: str):
    """
    Get suggested questions for the document
    """
    if session_id not in qa_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    qa = qa_sessions[session_id]
    suggestions = qa.get_suggested_questions()

    return {
        'success': True,
        'suggestions': suggestions
    }
