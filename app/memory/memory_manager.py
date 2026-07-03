import json
from sqlalchemy.orm import Session
from app.database.models import ChatHistory
from app.utils.logger import logger

class MemoryManager:
    """
    Manages persistent memory by loading historical contexts from SQLite.
    Formats conversation threads for consumption by LLM prompts.
    """
    
    @staticmethod
    def get_conversation_history(db: Session, student_id: str, limit: int = 5) -> str:
        """
        Fetches the last N queries and responses for the given student_id,
        ordering them chronologically.
        """
        try:
            records = (
                db.query(ChatHistory)
                .filter(ChatHistory.student_id == student_id)
                .order_by(ChatHistory.timestamp.desc())
                .limit(limit)
                .all()
            )
            
            # Reverse records to chronological order
            records = list(reversed(records))
            
            history_lines = []
            for r in records:
                # Try to parse the summary from the saved JSON response
                summary = ""
                try:
                    res_dict = json.loads(r.response)
                    summary = res_dict.get("summary", "")
                except Exception:
                    summary = r.response  # fallback to raw response if not JSON
                
                history_lines.append(f"User: {r.query}")
                history_lines.append(f"Assistant: {summary}")
                
            return "\n".join(history_lines)
            
        except Exception as e:
            logger.error(f"Error fetching conversation history for {student_id}: {str(e)}")
            return ""

    @staticmethod
    def save_chat(db: Session, student_id: str, query: str, intent: str, tool_used: str, response_json: str, execution_time: float) -> None:
        """
        Saves the complete conversation transaction to the SQLite database.
        """
        try:
            chat_record = ChatHistory(
                student_id=student_id,
                query=query,
                intent=intent,
                tool_used=tool_used,
                response=response_json,
                execution_time=execution_time
            )
            db.add(chat_record)
            db.commit()
            db.refresh(chat_record)
            logger.info(f"Saved chat history for student {student_id} to database.")
        except Exception as e:
            db.rollback()
            logger.error(f"Database error writing chat history: {str(e)}")
            raise
