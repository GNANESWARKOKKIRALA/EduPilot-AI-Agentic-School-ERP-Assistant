import json
from app.services.llm_service import LLMService
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.utils.logger import logger

class Reasoning:
    """
    AI Agent Reasoning component.
    Takes raw ERP tool outputs, planning history, and conversation memory
    to synthesize a coherent natural language response and evaluate overall status.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def synthesize_response(self, query: str, student_id: str, history: str, 
                            plan: list[str], intent: str, tool_names: list[str], 
                            tool_outputs: dict) -> tuple[dict, int]:
        """
        Runs LLM reasoning over tool data and returns the final structured dictionary
        along with token count.
        """
        logger.info(f"Synthesizing final response for query: '{query}'")

        # Format tool outputs for the LLM
        tool_outputs_str = json.dumps(tool_outputs, indent=2)
        plan_str = "\n".join([f"- {step}" for step in plan])
        
        user_message = (
            f"User Query: \"{query}\"\n"
            f"Student ID: \"{student_id}\"\n\n"
            f"Executed Plan:\n{plan_str}\n\n"
            f"Tool Output Payload:\n{tool_outputs_str}\n\n"
            f"Conversation History:\n{history if history else 'None'}\n\n"
            f"Please synthesize the final response. Keep it concise, conversational, and direct."
        )

        try:
            # Query the LLM for a natural language summary
            summary, tokens = self.llm_service.get_completion(
                system_message=SYSTEM_PROMPT,
                user_message=user_message,
                temperature=0.1
            )
        except Exception as e:
            logger.error(f"Failed to generate LLM reasoning summary: {str(e)}")
            summary = "I encountered an error generating the textual summary, but your ERP data is loaded below."
            tokens = 0

        # Programmatically evaluate the "status" metric from tool payloads
        status = self._determine_status(tool_outputs)

        # Map tool list to a nice display string
        tool_display_name = ", ".join([t.capitalize() + " Tool" for t in tool_names]) if tool_names else "None"

        # Build final structured response matching ChatResponse schema
        final_payload = {
            "intent": intent,
            "plan": plan,
            "tool": tool_display_name,
            "response": tool_outputs,
            "summary": summary.strip(),
            "status": status
        }
        
        return final_payload, tokens

    def _determine_status(self, tool_outputs: dict) -> str:
        """
        Determines the system status indicator based on data values (e.g. attendance percentage, fees status).
        """
        status_candidates = []

        # Check attendance
        if "attendance" in tool_outputs:
            att = tool_outputs["attendance"]
            pct = att.get("attendance_percentage", 100.0)
            if pct < 75.0:
                status_candidates.append("Critical")
            elif pct < 90.0:
                status_candidates.append("Warning")
            else:
                status_candidates.append("Good")

        # Check marks
        if "marks" in tool_outputs:
            marks = tool_outputs["marks"]
            avg = marks.get("analysis", {}).get("average_marks", 100.0)
            if avg < 50.0:
                status_candidates.append("Critical")
            elif avg < 65.0:
                status_candidates.append("Warning")
            else:
                status_candidates.append("Good")

        # Check fees
        if "fees" in tool_outputs:
            fees = tool_outputs["fees"]
            fee_status = fees.get("status", "Paid")
            pending = fees.get("pending_fees", 0)
            if fee_status.lower() == "pending" or pending > 0:
                status_candidates.append("Pending")
            else:
                status_candidates.append("Paid")

        # Check homework
        if "homework" in tool_outputs:
            hw = tool_outputs["homework"]
            pending_count = hw.get("pending_count", 0)
            due_tomorrow = hw.get("due_tomorrow_count", 0)
            if due_tomorrow > 0:
                status_candidates.append("Warning")
            elif pending_count > 2:
                status_candidates.append("Warning")
            else:
                status_candidates.append("Good")

        # Resolve candidates to a single status by priority: Critical > Pending > Warning > Paid > Good
        if "Critical" in status_candidates:
            return "Critical"
        if "Pending" in status_candidates:
            return "Pending"
        if "Warning" in status_candidates:
            return "Warning"
        if "Paid" in status_candidates:
            return "Paid"
        
        return "Good"
