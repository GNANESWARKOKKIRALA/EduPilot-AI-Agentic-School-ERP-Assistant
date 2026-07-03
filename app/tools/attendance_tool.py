import os
from datetime import datetime, timedelta
from app.utils.helpers import load_json_file
from app.utils.logger import logger

# Constants for term projection
TOTAL_TERM_DAYS = 150

class AttendanceTool:
    """
    ERP Tool to check student attendance logs.
    Includes calculations for 90% attendance maintenance and recent absences.
    """
    def __init__(self, data_path: str = "mock_data/attendance.json"):
        self.data_path = data_path

    def run(self, student_id: str) -> dict:
        """
        Executes the attendance check for a student.
        Returns a dictionary with attendance stats, recent absences, and 90% threshold logic.
        """
        logger.info(f"Running Attendance Tool for student {student_id}")
        data = load_json_file(self.data_path)
        
        if student_id not in data:
            logger.error(f"Student ID {student_id} not found in attendance database.")
            raise ValueError(f"Student ID {student_id} not found.")

        student_record = data[student_id]
        records = student_record.get("records", [])
        summary = student_record.get("summary", {})
        
        # Calculate last week's absences (last 7 days prior to current date 2026-07-03)
        # That means range [2026-06-26, 2026-07-02] inclusive
        current_date_str = "2026-07-03"
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
        last_week_start = current_date - timedelta(days=7)
        
        absences_last_week = []
        for r in records:
            r_date = datetime.strptime(r["date"], "%Y-%m-%d")
            if last_week_start <= r_date < current_date:
                if r["status"] == "Absent":
                    absences_last_week.append(r["date"])
                    
        # Calculate if they can maintain 90% attendance
        # Formula: (current_present + remaining_days) / TOTAL_TERM_DAYS >= 0.90
        present = summary.get("present", 0)
        absent = summary.get("absent", 0)
        total_days_logged = summary.get("total_days", 0)
        
        remaining_days = max(0, TOTAL_TERM_DAYS - total_days_logged)
        max_possible_present = present + remaining_days
        max_possible_percentage = round((max_possible_present / TOTAL_TERM_DAYS) * 100, 2)
        can_maintain_90 = max_possible_percentage >= 90.0
        
        required_days_to_reach_90 = max(0, int(0.9 * TOTAL_TERM_DAYS) - present)
        
        # Structure the calculations explanation
        projection_explanation = (
            f"Term total is {TOTAL_TERM_DAYS} days. Currently at {total_days_logged} days "
            f"({present} present, {absent} absent). With {remaining_days} days remaining, "
            f"attending all of them yields {max_possible_present}/{TOTAL_TERM_DAYS} present days, "
            f"making the maximum possible attendance {max_possible_percentage}%. "
            f"To reach the 90% requirement ({int(0.9 * TOTAL_TERM_DAYS)} present days), the student needs "
            f"to attend {required_days_to_reach_90} out of the remaining {remaining_days} days."
        )

        return {
            "student_name": student_record["student_name"],
            "class": student_record["class"],
            "attendance_percentage": summary.get("percentage", 0.0),
            "present": present,
            "absent": absent,
            "total_days_logged": total_days_logged,
            "absences_last_week": absences_last_week,
            "missed_classes_last_week_count": len(absences_last_week),
            "projection": {
                "total_term_days": TOTAL_TERM_DAYS,
                "remaining_days": remaining_days,
                "max_possible_percentage": max_possible_percentage,
                "can_maintain_90": can_maintain_90,
                "required_days_to_reach_90": required_days_to_reach_90,
                "explanation": projection_explanation
            }
        }
