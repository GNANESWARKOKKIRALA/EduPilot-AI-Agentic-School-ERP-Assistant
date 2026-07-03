import os
from app.tools.attendance_tool import AttendanceTool
from app.tools.marks_tool import MarksTool
from app.tools.homework_tool import HomeworkTool
from app.tools.fees_tool import FeesTool
from app.utils.logger import logger

class RecommendationTool:
    """
    ERP Tool that examines student performance data and compiles
    personalized actionable advice across academics, attendance, and tasks.
    """
    def __init__(self):
        self.attendance_tool = AttendanceTool()
        self.marks_tool = MarksTool()
        self.homework_tool = HomeworkTool()
        self.fees_tool = FeesTool()

    def run(self, student_id: str) -> dict:
        """
        Runs diagnostic analysis and returns structured recommendation objects.
        """
        logger.info(f"Running Smart Recommendation Tool for student {student_id}")
        
        attendance_res = self.attendance_tool.run(student_id)
        marks_res = self.marks_tool.run(student_id)
        homework_res = self.homework_tool.run(student_id)
        fees_res = self.fees_tool.run(student_id)
        
        recommendations = []
        
        # 1. Attendance Analysis
        att_pct = attendance_res.get("attendance_percentage", 0.0)
        proj = attendance_res.get("projection", {})
        if att_pct < 85.0:
            recommendations.append({
                "category": "Attendance",
                "severity": "High",
                "message": (
                    f"Your attendance is critically low at {att_pct}%. "
                    f"To maintain the mandatory 90% attendance, you must attend at least "
                    f"{proj.get('required_days_to_reach_90', 0)} out of the remaining {proj.get('remaining_days', 0)} term days."
                )
            })
        elif att_pct < 90.0:
            recommendations.append({
                "category": "Attendance",
                "severity": "Medium",
                "message": (
                    f"Your attendance is at {att_pct}%. You are close to the 90% benchmark. "
                    f"Avoid taking any unnecessary leaves."
                )
            })
        else:
            recommendations.append({
                "category": "Attendance",
                "severity": "Low",
                "message": f"Great job maintaining a strong attendance rate of {att_pct}%."
            })
            
        # 2. Academic Marks Analysis
        analysis = marks_res.get("analysis", {})
        midterm_marks = marks_res.get("exams", {}).get("Midterm", {})
        weak_subjects = analysis.get("weak_subjects", [])
        avg_marks = analysis.get("average_marks", 0.0)
        schedule = marks_res.get("study_planner", {}).get("schedule", {})
        
        if weak_subjects:
            for subj in weak_subjects:
                subj_score = midterm_marks.get(subj, 0)
                daily_hrs = schedule.get(subj, {}).get("daily_study_hours_allocated", 1.0)
                recommendations.append({
                    "category": "Academic",
                    "severity": "High",
                    "message": (
                        f"Critical focus needed in {subj} (Midterm Score: {subj_score}%). "
                        f"Dedicate at least {daily_hrs} hours daily as allocated in your study planner."
                    )
                })
        else:
            recommendations.append({
                "category": "Academic",
                "severity": "Low",
                "message": f"Your overall academic average is healthy ({avg_marks}%). Keep studying consistently."
            })
            
        # 3. Homework Analysis
        pending_hw = homework_res.get("pending_count", 0)
        due_tomorrow = homework_res.get("due_tomorrow_count", 0)
        if pending_hw > 0:
            severity = "High" if due_tomorrow > 0 else "Medium"
            due_tomorrow_msg = f" ({due_tomorrow} due tomorrow!)" if due_tomorrow > 0 else ""
            recommendations.append({
                "category": "Homework",
                "severity": severity,
                "message": f"You have {pending_hw} pending homework assignment(s){due_tomorrow_msg}. Complete them today."
            })
            
        # 4. Financial Dues Analysis
        pending_fees = fees_res.get("pending_fees", 0)
        if pending_fees > 0:
            recommendations.append({
                "category": "Fees",
                "severity": "Medium",
                "message": f"You have outstanding dues of {pending_fees} INR. Please pay before the due date {fees_res.get('due_date')}."
            })
            
        return {
            "student_name": attendance_res.get("student_name"),
            "class": attendance_res.get("class"),
            "recommendations": recommendations
        }
