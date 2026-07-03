from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatResponse(BaseModel):
    """
    Response model returned by the /chat endpoint.
    Consists of the detected intent, step-by-step planner execution steps,
    selected tool names, the raw data payload, a conversational summary, and status.
    """
    intent: str = Field(..., description="Detected user intent, e.g., 'Attendance' or 'Multi-intent'")
    plan: List[str] = Field(..., description="Execution steps decided by the AI planner")
    tool: str = Field(..., description="Selected ERP tools executed")
    response: Dict[str, Any] = Field(..., description="Aggregated raw tool response payload")
    summary: str = Field(..., description="Natural language response synthesized by the AI agent")
    status: str = Field(..., description="Status health feedback (e.g., 'Good', 'Pending', 'Paid', 'Error')")

class ChatHistoryItem(BaseModel):
    """
    Response model for individual records returned from the chat history endpoint.
    """
    id: int = Field(..., description="Database primary key id")
    student_id: str = Field(..., description="The student identifier associated with this query")
    query: str = Field(..., description="The user's original query")
    intent: Optional[str] = Field(None, description="The detected intent of the query")
    tool_used: Optional[str] = Field(None, description="The name of the tool(s) utilized")
    response: Dict[str, Any] = Field(..., description="The parsed JSON response object")
    timestamp: str = Field(..., description="ISO format datetime of when the transaction occurred")
    execution_time: Optional[float] = Field(None, description="Time in seconds taken to process request")
