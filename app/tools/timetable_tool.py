import os
from app.utils.helpers import load_json_file
from app.utils.logger import logger

class TimetableTool:
    """
    ERP Tool to check class schedules, teachers, and timings.
    Resolves the student's class and returns their daily or weekly roster.
    """
    def __init__(self, timetable_path: str = "mock_data/timetable.json", student_meta_path: str = "mock_data/attendance.json"):
        self.timetable_path = timetable_path
        self.student_meta_path = student_meta_path

    def run(self, student_id: str, day_filter: str = None) -> dict:
        """
        Retrieves the timetable for a student's class.
        Optionally filters by a specific day (e.g. 'Monday').
        """
        logger.info(f"Running Timetable Tool for student {student_id}")
        
        # 1. Resolve student's class from the student metadata database (attendance.json)
        student_db = load_json_file(self.student_meta_path)
        if student_id not in student_db:
            logger.error(f"Student ID {student_id} not found in student database.")
            raise ValueError(f"Student ID {student_id} not found.")
            
        student_record = student_db[student_id]
        student_class = student_record.get("class")
        student_name = student_record.get("student_name")
        
        # 2. Retrieve timetable entries for that class
        timetable_db = load_json_file(self.timetable_path)
        if student_class not in timetable_db:
            logger.error(f"No timetable found for class {student_class}.")
            raise ValueError(f"Timetable for class {student_class} not found.")
            
        class_timetable = timetable_db[student_class]
        
        # Apply day filters if requested (case-insensitive match)
        filtered_timetable = class_timetable
        if day_filter:
            day_clean = day_filter.lower().strip()
            # Resolve 'today', 'current', 'now' keywords to the current weekday
            if day_clean in ["today", "current", "now"]:
                from datetime import datetime
                day_clean = datetime.now().strftime("%A").lower()
                
            matched_key = None
            for key in class_timetable.keys():
                if key.lower() == day_clean:
                    matched_key = key
                    break
                    
            if matched_key:
                filtered_timetable = {matched_key: class_timetable[matched_key]}
            else:
                # Fall back to returning the full weekly timetable instead of empty dictionary
                filtered_timetable = class_timetable
                
        return {
            "student_name": student_name,
            "class": student_class,
            "day_filter": day_filter,
            "timetable": filtered_timetable
        }
