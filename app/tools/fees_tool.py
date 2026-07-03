import os
from app.utils.helpers import load_json_file
from app.utils.logger import logger

class FeesTool:
    """
    ERP Tool to check tuition fee status and transactions.
    """
    def __init__(self, data_path: str = "mock_data/fees.json"):
        self.data_path = data_path

    def run(self, student_id: str) -> dict:
        """
        Retrieves payment ledger details for the student.
        Returns a dictionary. Never generates natural language.
        """
        logger.info(f"Running Fees Tool for student {student_id}")
        data = load_json_file(self.data_path)
        
        if student_id not in data:
            logger.error(f"Student ID {student_id} not found in fees database.")
            raise ValueError(f"Student ID {student_id} not found.")

        student_record = data[student_id]
        
        return {
            "student_name": student_record.get("student_name"),
            "class": student_record.get("class"),
            "total_fees": student_record.get("total_fees", 0),
            "paid_fees": student_record.get("paid_fees", 0),
            "pending_fees": student_record.get("pending_fees", 0),
            "due_date": student_record.get("due_date", ""),
            "status": student_record.get("status", "Pending"),
            "transactions": student_record.get("transactions", [])
        }
