import os
from app.tools.attendance_tool import AttendanceTool
from app.tools.marks_tool import MarksTool
from app.tools.homework_tool import HomeworkTool
from app.tools.fees_tool import FeesTool
from app.utils.logger import logger

class PerformanceTool:
    """
    ERP Tool that aggregates metrics from other tools to assemble
    a comprehensive student performance dashboard. Used to support
    Academic Performance Summaries and Parent Progress Reports.
    """
    def __init__(self):
        self.attendance_tool = AttendanceTool()
        self.marks_tool = MarksTool()
        self.homework_tool = HomeworkTool()
        self.fees_tool = FeesTool()

    def run(self, student_id: str) -> dict:
        """
        Gathers metrics from all student logs to return a unified academic dashboard.
        """
        logger.info(f"Running Performance Aggregation Tool for student {student_id}")
        
        # Invoke individual tools programmatically
        attendance_res = self.attendance_tool.run(student_id)
        marks_res = self.marks_tool.run(student_id)
        homework_res = self.homework_tool.run(student_id)
        fees_res = self.fees_tool.run(student_id)
        
        # Extract individual analysis elements
        avg_marks = marks_res["analysis"].get("average_marks", 0.0)
        highest_subj = marks_res["analysis"].get("highest_subject", "N/A")
        highest_score = marks_res["analysis"].get("highest_score", 0)
        lowest_subj = marks_res["analysis"].get("lowest_subject", "N/A")
        lowest_score = marks_res["analysis"].get("lowest_score", 0)
        
        attendance_percentage = attendance_res.get("attendance_percentage", 0.0)
        pending_hw_count = homework_res.get("pending_count", 0)
        pending_fees = fees_res.get("pending_fees", 0)
        fee_status = fees_res.get("status", "Pending")
        
        # Inferred academic standing
        if avg_marks >= 85 and attendance_percentage >= 90:
            academic_standing = "Excellent"
        elif avg_marks >= 60 and attendance_percentage >= 75:
            academic_standing = "Average"
        else:
            academic_standing = "Needs Attention"
            
        return {
            "student_name": attendance_res["student_name"],
            "class": attendance_res["class"],
            "academic_summary": {
                "average_marks": avg_marks,
                "highest_subject": highest_subj,
                "highest_score": highest_score,
                "lowest_subject": lowest_subj,
                "lowest_score": lowest_score,
                "attendance_percentage": attendance_percentage,
                "pending_homework_count": pending_hw_count,
                "pending_fees": pending_fees,
                "fee_status": fee_status,
                "academic_standing": academic_standing
            },
            "parent_report": {
                "attendance_summary": f"{attendance_percentage}% attendance ({attendance_res['present']} present, {attendance_res['absent']} absent)",
                "marks_summary": f"Average: {avg_marks}%. Strongest: {highest_subj} ({highest_score}%). Weakest: {lowest_subj} ({lowest_score}%)",
                "homework_summary": f"{pending_hw_count} assignments pending out of {homework_res['total_assignments']}",
                "fee_status": f"Dues: {pending_fees} INR. Status: {fee_status} (Due: {fees_res['due_date']})",
                "overall_performance": academic_standing
            }
        }
