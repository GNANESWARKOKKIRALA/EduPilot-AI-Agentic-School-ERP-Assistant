import time
import json
from sqlalchemy.orm import Session
from app.services.llm_service import LLMService
from app.agents.planner import Planner
from app.agents.executor import Executor
from app.agents.reasoning import Reasoning
from app.memory.memory_manager import MemoryManager
from app.database.models import ExecutionLog
from app.utils.logger import logger

class ChatService:
    """
    Service layer coordinating the Agentic loop.
    Loads context -> Plan -> Execute -> Reason -> Save logs/history -> Return payload.
    """
    def __init__(self, api_key: str = None):
        self.llm_service = LLMService(api_key=api_key)
        self.planner = Planner(self.llm_service)
        self.executor = Executor()
        self.reasoning = Reasoning(self.llm_service)

    def process_user_message(self, db: Session, student_id: str, message: str) -> dict:
        """
        Orchestrates intent classification, planning, tool execution,
        and natural language reply synthesis. Logs runtime metrics.
        """
        start_time = time.perf_counter()
        
        # 1. Fetch memory/context history
        logger.info(f"Loading history for student {student_id}")
        conversation_history = MemoryManager.get_conversation_history(db, student_id=student_id)
        
        total_tokens = 0
        errors = None
        plan_dict = {}
        tool_outputs = {}
        executed_tools = []
        
        try:
            # 2. Planning phase
            logger.info("Starting Agent Planning phase")
            plan_dict, plan_tokens = self.planner.generate_plan(
                query=message,
                student_id=student_id,
                history=conversation_history
            )
            total_tokens += plan_tokens
            
            intent = plan_dict.get("intent", "Unknown")
            selected_tools = plan_dict.get("tools", [])
            plan_steps = plan_dict.get("plan", [])
            entities = plan_dict.get("entities", {})
            
            # 3. Execution phase (calling tools)
            logger.info(f"Starting Agent Execution phase for tools: {selected_tools}")
            tool_outputs, executed_tools = self.executor.execute_tools(
                tool_names=selected_tools,
                student_id=student_id,
                entities=entities
            )
            
            # 4. Reasoning phase (LLM text synthesis)
            logger.info("Starting Agent Reasoning synthesis phase")
            final_payload, reasoning_tokens = self.reasoning.synthesize_response(
                query=message,
                student_id=student_id,
                history=conversation_history,
                plan=plan_steps,
                intent=intent,
                tool_names=executed_tools,
                tool_outputs=tool_outputs
            )
            total_tokens += reasoning_tokens
            
        except Exception as e:
            logger.error(f"Unhandled exception in agent lifecycle: {str(e)}", exc_info=True)
            errors = str(e)
            
            # Formulate fallback JSON response in case of developer code exceptions
            final_payload = {
                "intent": "Error",
                "plan": ["Initiated query analysis", "Internal error occurred during lifecycle execution"],
                "tool": "System Error Handler",
                "response": {
                    "error": "Failed to complete processing",
                    "details": str(e)
                },
                "summary": "I apologize, but I ran into a system error processing your request. Please try again shortly.",
                "status": "Critical"
            }
            
        # 5. Stop watch and finalize timers
        elapsed_seconds = time.perf_counter() - start_time
        final_payload["execution_time"] = round(elapsed_seconds, 4)
        
        # 6. Database Logging
        # A: Save Chat History (for future memory context)
        serialized_response = json.dumps(final_payload)
        try:
            MemoryManager.save_chat(
                db=db,
                student_id=student_id,
                query=message,
                intent=final_payload["intent"],
                tool_used=final_payload["tool"],
                response_json=serialized_response,
                execution_time=elapsed_seconds
            )
        except Exception as ex:
            logger.error(f"Failed to record Chat History record: {str(ex)}")

        # B: Save Execution Log (internal metrics dashboard)
        try:
            execution_log = ExecutionLog(
                student_id=student_id,
                query=message,
                intent=final_payload["intent"],
                tool_used=final_payload["tool"],
                execution_plan=json.dumps(final_payload["plan"]),
                execution_time=elapsed_seconds,
                errors=errors,
                llm_tokens=total_tokens,
                response=final_payload["summary"]
            )
            db.add(execution_log)
            db.commit()
            logger.info("Saved execution log entry successfully.")
        except Exception as ex:
            db.rollback()
            logger.error(f"Failed to record Execution Log record: {str(ex)}")
            
        return final_payload
