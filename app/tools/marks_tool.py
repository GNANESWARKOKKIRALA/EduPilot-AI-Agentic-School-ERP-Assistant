import os
from app.utils.helpers import load_json_file
from app.utils.logger import logger

class MarksTool:
    """
    ERP Tool to check and analyze student academic marks.
    Features automated weak subject identification and study planners.
    """
    def __init__(self, data_path: str = "mock_data/marks.json"):
        self.data_path = data_path

    def run(self, student_id: str, exam_days_remaining: int = 30, daily_hours: float = 3.0) -> dict:
        """
        Processes exam scores to generate statistical analysis and a custom study schedule.
        Returns a dictionary. Never generates natural language.
        """
        logger.info(f"Running Marks Tool for student {student_id}")
        data = load_json_file(self.data_path)
        
        if student_id not in data:
            logger.error(f"Student ID {student_id} not found in marks database.")
            raise ValueError(f"Student ID {student_id} not found.")

        student_record = data[student_id]
        exams = student_record.get("exams", {})
        
        # Baseline analysis on the latest exam 'Midterm'
        midterm = exams.get("Midterm", {})
        if not midterm:
            logger.warning(f"No Midterm results found for student {student_id}.")
            return {
                "student_name": student_record["student_name"],
                "class": student_record["class"],
                "exams": exams,
                "analysis": {},
                "study_planner": {}
            }

        scores = list(midterm.values())
        avg_marks = round(sum(scores) / len(scores), 2)
        
        # Calculate highest and lowest subjects
        highest_subject = max(midterm, key=midterm.get)
        highest_score = midterm[highest_subject]
        
        lowest_subject = min(midterm, key=midterm.get)
        lowest_score = midterm[lowest_subject]
        
        # Classify strengths and weaknesses
        # Weak: < 65, Strong: >= 85
        weak_subjects = [subj for subj, score in midterm.items() if score < 65]
        strong_subjects = [subj for subj, score in midterm.items() if score >= 85]
        
        # Study Planner Hour Allocation Algorithm
        # Weights are inversely proportional to score: priority_weight = (100 - score)
        # Higher weights receive a larger portion of the total available hours.
        total_hours = exam_days_remaining * daily_hours
        study_schedule = {}
        
        weights = {}
        for subj, score in midterm.items():
            # Guarantee at least a minimal weight of 10 to strong subjects
            weights[subj] = max(10, 100 - score)
            
        total_weight = sum(weights.values())
        
        for subj, score in midterm.items():
            allocated_ratio = weights[subj] / total_weight
            allocated_hours = round(total_hours * allocated_ratio, 1)
            daily_allocation = round(allocated_hours / exam_days_remaining, 2)
            
            if subj in weak_subjects:
                priority = "High"
            elif subj in strong_subjects:
                priority = "Low"
            else:
                priority = "Medium"
                
            study_schedule[subj] = {
                "current_score": score,
                "priority": priority,
                "total_study_hours_allocated": allocated_hours,
                "daily_study_hours_allocated": daily_allocation
            }
            
        return {
            "student_name": student_record["student_name"],
            "class": student_record["class"],
            "exams": exams,
            "analysis": {
                "average_marks": avg_marks,
                "highest_subject": highest_subject,
                "highest_score": highest_score,
                "lowest_subject": lowest_subject,
                "lowest_score": lowest_score,
                "weak_subjects": weak_subjects,
                "strong_subjects": strong_subjects
            },
            "study_planner": {
                "exam_days_remaining": exam_days_remaining,
                "daily_hours_available": daily_hours,
                "total_hours_available_for_term": total_hours,
                "schedule": study_schedule
            }
        }
