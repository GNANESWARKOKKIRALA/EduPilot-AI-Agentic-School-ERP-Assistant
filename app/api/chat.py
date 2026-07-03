import json
import os
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.services.chat_service import ChatService
from app.database.database import get_db
from app.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat"])

def check_student_exists(student_id: str):
    """
    Validates if the student ID exists in the mock database keys.
    Raises ValueError if not present.
    """
    db_path = "mock_data/attendance.json"
    if not os.path.exists(db_path):
        # Database file hasn't been created yet, allow through
        return
        
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            students = json.load(f)
            if student_id not in students:
                raise ValueError(f"Student ID '{student_id}' is invalid or does not exist in ERP records.")
    except json.JSONDecodeError:
        logger.error("JSON decode error during student ID pre-validation.")
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        logger.error(f"Error checking student ID: {str(e)}")

@router.post("", response_model=ChatResponse)
def post_chat(request: ChatRequest, db: Session = Depends(get_db), x_groq_api_key: Optional[str] = Header(None)):
    """
    POST /chat
    Executes intent classification, planning, tool running,
    and returns a structured Agentic ERP response.
    session_id is required for multi-user conversation isolation.
    """
    logger.info(f"Received API chat request for session: {request.session_id}, student: {request.student_id}")
    
    # 1. Input pre-validation
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User query message cannot be empty."
        )
        
    try:
        check_student_exists(request.student_id)
    except ValueError as ve:
        logger.warning(f"Validation failure: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
        
    # 2. Run Agentic Loop (with session_id for isolation)
    try:
        service = ChatService(api_key=x_groq_api_key)
        response_payload = service.process_user_message(
            db=db,
            session_id=request.session_id,
            student_id=request.student_id,
            message=request.message
        )
        return response_payload
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in the agentic brain: {str(e)}"
        )
