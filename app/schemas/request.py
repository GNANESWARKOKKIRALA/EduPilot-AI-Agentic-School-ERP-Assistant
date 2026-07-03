from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.
    Validates that a query contains student_id and message fields.
    """
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
