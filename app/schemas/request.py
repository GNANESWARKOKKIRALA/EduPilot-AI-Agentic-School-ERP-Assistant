from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.
    Validates that a query contains session_id, student_id, and message fields.
    """
    session_id: str = Field(
        ...,
        description="Unique browser session identifier (UUID) for multi-user isolation",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    student_id: str = Field(
        ..., 
        description="The student identifier, e.g., ST101",
        examples=["ST101"]
    )
    message: str = Field(
        ..., 
        description="The natural language query from the user",
        examples=["Show my attendance this month."]
    )
