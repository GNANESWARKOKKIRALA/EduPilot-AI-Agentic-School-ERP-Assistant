import json
from app.services.llm_service import LLMService
from app.prompts.planner_prompt import PLANNER_PROMPT
from app.utils.logger import logger

class Planner:
    """
    AI Agent Planner component.
    Leverages LLM JSON completion to translate natural language user queries
    and conversation history into structured execution plans.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def generate_plan(self, query: str, student_id: str, history: str) -> tuple[dict, int]:
        """
        Interacts with the LLM to get a structured execution plan.
        Returns a tuple of (plan_dictionary, token_count).
        """
        logger.info(f"Creating execution plan for student {student_id}")
        
        # Format the planning prompt with current states
        formatted_prompt = PLANNER_PROMPT.format(
            student_id=student_id,
            query=query,
            history=history if history else "None (First interaction)"
        )
        
        try:
            # Query LLM with JSON mode forced
            plan_dict, tokens = self.llm_service.get_json_completion(formatted_prompt)
            
            # Post-validation of keys to ensure standard contract
            required_keys = ["intent", "confidence", "entities", "tools", "plan"]
            for key in required_keys:
                if key not in plan_dict:
                    plan_dict[key] = None if key != "tools" and key != "plan" else []
            
            logger.info(f"Planner successfully compiled plan for intent: {plan_dict['intent']}")
            return plan_dict, tokens
            
        except Exception as e:
            logger.error(f"Error during agent planning execution: {str(e)}")
            # Fail-safe plan fallback in case of LLM failure
            fallback_plan = {
                "intent": "Unknown",
                "confidence": 0.0,
                "entities": {},
                "tools": [],
                "plan": ["Attempt fallback search", "Log planning exception"],
                "error": str(e)
            }
            return fallback_plan, 0
