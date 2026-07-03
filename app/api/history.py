import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.response import ChatHistoryItem
from app.database.database import get_db
from app.database.models import ChatHistory
from app.utils.logger import logger

router = APIRouter(prefix="/chat/history", tags=["History"])

@router.get("", response_model=List[ChatHistoryItem])
def get_history(
    session_id: str = Query(..., description="Required unique session ID for user-isolated history retrieval"),
    student_id: str = Query(None, description="Filter conversation logs by student ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of historical records to return"),
    db: Session = Depends(get_db)
):
    """
    GET /chat/history
    Fetches chat logs stored in the SQLite database.
    REQUIRES session_id to ensure only the requesting user's conversations are returned.
    Can be additionally filtered by student_id.
    """
    logger.info(f"Fetching history records (session={session_id}, limit={limit}, student_filter={student_id})")
    
    query_builder = db.query(ChatHistory).filter(ChatHistory.session_id == session_id)
    if student_id:
        query_builder = query_builder.filter(ChatHistory.student_id == student_id)
        
    # Get latest records first
    records = query_builder.order_by(ChatHistory.timestamp.desc()).limit(limit).all()
    
    history_items = []
    for r in records:
        try:
            # Parse the serialized response payload string back into a dictionary
            parsed_response = json.loads(r.response)
        except Exception:
            parsed_response = {
                "summary": r.response,
                "error": "Failed to parse database record JSON payload."
            }
            
        formatted_time = r.timestamp.isoformat() if r.timestamp else ""
        
        history_items.append(
            ChatHistoryItem(
                id=r.id,
                student_id=r.student_id,
                query=r.query,
                intent=r.intent,
                tool_used=r.tool_used,
                response=parsed_response,
                timestamp=formatted_time,
                execution_time=r.execution_time
            )
        )
        
    return history_items
