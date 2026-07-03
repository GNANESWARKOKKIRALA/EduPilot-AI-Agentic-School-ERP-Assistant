import os
from datetime import datetime, timedelta
from app.utils.helpers import load_json_file
from app.utils.logger import logger

class HomeworkTool:
    """
    ERP Tool to check and filter student homework assignments.
    Supports status-based queries and deadline-based filtering (e.g. due tomorrow).
    """
    def __init__(self, data_path: str = "mock_data/homework.json"):
        self.data_path = data_path

    def run(self, student_id: str, status_filter: str = None, due_date_filter: str = None) -> dict:
        """
        Retrieves homework tasks.
        Filters list by status or specific due date (supports 'tomorrow' matching 2026-07-04).
        """
        logger.info(f"Running Homework Tool for student {student_id}")
        data = load_json_file(self.data_path)
        
        if student_id not in data:
            logger.error(f"Student ID {student_id} not found in homework database.")
            raise ValueError(f"Student ID {student_id} not found.")

        student_record = data[student_id]
        homework_list = student_record.get("homework_list", [])
        
        # System baseline date is July 3rd, 2026
        today_str = "2026-07-03"
        tomorrow_str = "2026-07-04"
        
        pending_tasks = [hw for hw in homework_list if hw.get("status") == "Pending"]
        completed_tasks = [hw for hw in homework_list if hw.get("status") == "Completed"]
        due_tomorrow_tasks = [hw for hw in homework_list if hw.get("due_date") == tomorrow_str]
        
        # Apply filtering
        filtered_list = homework_list
        if status_filter:
            filtered_list = [
                hw for hw in filtered_list 
                if hw.get("status", "").lower() == status_filter.lower()
            ]
            
        if due_date_filter:
            target_date = tomorrow_str if due_date_filter.lower() == "tomorrow" else due_date_filter
            filtered_list = [
                hw for hw in filtered_list 
                if hw.get("due_date") == target_date
            ]
            
        return {
            "student_name": student_record.get("student_name"),
            "class": student_record.get("class"),
            "total_assignments": len(homework_list),
            "pending_count": len(pending_tasks),
            "completed_count": len(completed_tasks),
            "due_tomorrow_count": len(due_tomorrow_tasks),
            "due_tomorrow_assignments": due_tomorrow_tasks,
            "pending_assignments": pending_tasks,
            "filtered_assignments": filtered_list
        }
