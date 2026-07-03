from app.tools.attendance_tool import AttendanceTool
from app.tools.marks_tool import MarksTool
from app.tools.fees_tool import FeesTool
from app.tools.homework_tool import HomeworkTool
from app.tools.timetable_tool import TimetableTool
from app.tools.performance_tool import PerformanceTool
from app.tools.recommendation_tool import RecommendationTool
from app.utils.logger import logger

class Executor:
    """
    AI Agent Executor component.
    Resolves tool strings to class instances and executes them sequentially.
    Supports multi-tool requests by merging execution outputs.
    """
    def __init__(self):
        # Register available tools
        self.registry = {
            "attendance": AttendanceTool(),
            "marks": MarksTool(),
            "fees": FeesTool(),
            "homework": HomeworkTool(),
            "timetable": TimetableTool(),
            "performance": PerformanceTool(),
            "recommendation": RecommendationTool()
        }

    def execute_tools(self, tool_names: list[str], student_id: str, entities: dict) -> tuple[dict, list[str]]:
        """
        Runs the specified tools sequentially and merges their outputs.
        Extracts appropriate parameters from parsed entities.
        """
        results = {}
        executed_successfully = []
        
        # Safe default if no tools selected
        if not tool_names:
            logger.warning("No tools selected by the planner. Running fallback.")
            return {"message": "No tool was executed. Please specify an action."}, []

        for tool_name in tool_names:
            tool_name = tool_name.lower().strip()
            if tool_name not in self.registry:
                logger.warning(f"Requested tool '{tool_name}' is not in the registry.")
                results[tool_name] = {"error": f"Tool '{tool_name}' is not supported."}
                continue
                
            tool_instance = self.registry[tool_name]
            
            # Extract arguments tailored for each tool
            kwargs = {}
            try:
                if tool_name == "homework":
                    # Check for status (e.g. 'Pending') or due date queries (e.g. 'tomorrow')
                    status = entities.get("status") or entities.get("homework_status")
                    due = entities.get("due_date") or entities.get("time_range") or entities.get("day")
                    if status:
                        kwargs["status_filter"] = str(status)
                    if due:
                        kwargs["due_date_filter"] = str(due)
                        
                elif tool_name == "timetable":
                    # Check for day queries (e.g. 'Monday')
                    day = entities.get("day") or entities.get("weekday") or entities.get("time_range")
                    if day:
                        kwargs["day_filter"] = str(day)
                        
                elif tool_name == "marks":
                    # Parse study planner limits if user asks for exam study plan
                    days_rem = entities.get("exam_days_remaining") or entities.get("days_remaining")
                    hrs = entities.get("daily_hours") or entities.get("study_hours") or entities.get("hours")
                    if days_rem:
                        try:
                            kwargs["exam_days_remaining"] = int(days_rem)
                        except (ValueError, TypeError):
                            pass
                    if hrs:
                        try:
                            kwargs["daily_hours"] = float(hrs)
                        except (ValueError, TypeError):
                            pass
                
                logger.info(f"Invoking {tool_name} with kwargs: {kwargs}")
                
                # Execute the tool and capture return payload
                tool_output = tool_instance.run(student_id, **kwargs)
                results[tool_name] = tool_output
                executed_successfully.append(tool_name)
                
            except Exception as e:
                logger.error(f"Execution error on tool '{tool_name}': {str(e)}")
                results[tool_name] = {
                    "error": f"Failed to retrieve data from {tool_name} tool.",
                    "details": str(e)
                }
                
        return results, executed_successfully
