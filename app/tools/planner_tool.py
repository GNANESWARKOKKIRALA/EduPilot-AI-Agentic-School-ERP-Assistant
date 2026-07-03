from app.utils.logger import logger

class PlannerTool:
    """
    ERP Tool representing the agent planner interface.
    Used to audit, format, or debug execution plans programmatically.
    """
    def __init__(self):
        pass

    def run(self, student_id: str, plan_steps: list[str]) -> dict:
        """
        Formats and returns active execution plan steps.
        Never generates natural language.
        """
        logger.info(f"Running Planner Tool helper for student {student_id}")
        return {
            "student_id": student_id,
            "status": "Plan Validated",
            "steps_count": len(plan_steps),
            "steps": plan_steps
        }
