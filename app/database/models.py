from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.database.database import Base

class ChatHistory(Base):
    """
    Model for storing conversation history.
    Saves the user request and corresponding response schema returned to frontend.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    query = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    tool_used = Column(String(200), nullable=True)
    response = Column(Text, nullable=False)  # Serialized JSON of response
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    execution_time = Column(Float, nullable=True)

class ExecutionLog(Base):
    """
    Model for storing detailed system performance and agent reasoning logs.
    Captures execution planning, errors, response times, and LLM usage.
    """
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    query = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    tool_used = Column(String(200), nullable=True)
    execution_plan = Column(Text, nullable=True)  # Serialized JSON list of plan steps
    execution_time = Column(Float, nullable=False)  # Time taken in seconds
    errors = Column(Text, nullable=True)
    llm_tokens = Column(Integer, nullable=True)  # Token count if available
    response = Column(Text, nullable=True)  # The generated final response text
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
