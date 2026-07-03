import os
import json
import random
from datetime import datetime, timedelta

def generate_data():
    os.makedirs("mock_data", exist_ok=True)
    
    # 20 Students lists
    student_ids = [f"ST{i:03d}" for i in range(101, 121)]
    student_names = [
        "Aarav Mehta", "Diya Sharma", "Ishaan Patel", "Ananya Iyer",
        "Kabir Joshi", "Meera Nair", "Rohan Gupta", "Siddharth Rao",
        "Tara Deshmukh", "Aditya Kulkarni", "Neha Verma", "Vivaan Kapoor",
        "Riya Sen", "Arjun Reddy", "Kavya Bhat", "Sai Prasad",
        "Pranav Pillai", "Shruti Hegde", "Dev Shah", "Alisha Das"
    ]
    
    # Classes: 10-A and 10-B
    student_class_map = {}
    for i, sid in enumerate(student_ids):
        student_class_map[sid] = "10-A" if i % 2 == 0 else "10-B"
        
    start_date = datetime(2026, 6, 1)  # Current term starts from June 1st, 2026
    current_date = datetime(2026, 7, 3) # Today's date is July 3rd, 2026
    
    # --- 1. Attendance Data ---
    attendance_data = {}
    
    # Generate daily attendance records
    delta = current_date - start_date
    total_school_days = 0
    date_list = []
    for d in range(delta.days + 1):
        day = start_date + timedelta(days=d)
        if day.weekday() < 5:  # Monday to Friday
            date_list.append(day.strftime("%Y-%m-%d"))
            total_school_days += 1

    for sid, name in zip(student_ids, student_names):
        records = []
        present_count = 0
        absent_count = 0
        
        # Base attendance rate (between 75% and 98%)
        base_rate = random.uniform(0.75, 0.98)
        
        # Last week range: 2026-06-22 to 2026-06-28 or similar
        # Let's say last week is 2026-06-22 to 2026-06-26 (school days)
        for dt_str in date_list:
            if random.random() < base_rate:
                status = "Present"
                present_count += 1
            else:
                status = "Absent"
                absent_count += 1
            records.append({"date": dt_str, "status": status})
            
        attendance_data[sid] = {
            "student_name": name,
            "class": student_class_map[sid],
            "records": records,
            "summary": {
                "total_days": total_school_days,
                "present": present_count,
                "absent": absent_count,
                "percentage": round((present_count / total_school_days) * 100, 2)
            }
        }
        
    with open("mock_data/attendance.json", "w", encoding="utf-8") as f:
        json.dump(attendance_data, f, indent=2)

    # --- 2. Marks Data ---
    marks_data = {}
    subjects = ["Mathematics", "Science", "English", "Social Studies", "Computer Science"]
    for sid, name in zip(student_ids, student_names):
        # Generate marks for Midterm and Unit Test 1
        midterm_marks = {}
        ut_marks = {}
        
        # Determine student strength: some excel, some average, some weak
        profile = random.choice(["excellent", "average", "weak_math", "weak_science"])
        
        for subj in subjects:
            if profile == "excellent":
                m_score = random.randint(85, 100)
                u_score = random.randint(18, 20)  # out of 20
            elif profile == "weak_math" and subj == "Mathematics":
                m_score = random.randint(40, 55)
                u_score = random.randint(8, 11)
            elif profile == "weak_science" and subj == "Science":
                m_score = random.randint(35, 55)
                u_score = random.randint(7, 11)
            else:
                m_score = random.randint(60, 85)
                u_score = random.randint(12, 17)
                
            midterm_marks[subj] = m_score
            ut_marks[subj] = u_score * 5  # normalized to 100
            
        marks_data[sid] = {
            "student_name": name,
            "class": student_class_map[sid],
            "exams": {
                "Unit Test 1": ut_marks,
                "Midterm": midterm_marks
            }
        }
        
    with open("mock_data/marks.json", "w", encoding="utf-8") as f:
        json.dump(marks_data, f, indent=2)

    # --- 3. Fees Data ---
    fees_data = {}
    for sid, name in zip(student_ids, student_names):
        total_fees = 12000
        # Randomize payment status
        rand_status = random.choice(["Paid", "Pending", "Pending"])
        
        if rand_status == "Paid":
            paid_fees = total_fees
            pending_fees = 0
            status = "Paid"
            txns = [
                {"id": f"TXN{random.randint(10000, 99999)}", "amount": 6000, "date": "2026-06-05", "status": "Success"},
                {"id": f"TXN{random.randint(10000, 99999)}", "amount": 6000, "date": "2026-06-28", "status": "Success"}
            ]
        else:
            paid_fees = 6000
            pending_fees = 6000
            status = "Pending"
            txns = [
                {"id": f"TXN{random.randint(10000, 99999)}", "amount": 6000, "date": "2026-06-05", "status": "Success"}
            ]
            
        fees_data[sid] = {
            "student_name": name,
            "class": student_class_map[sid],
            "total_fees": total_fees,
            "paid_fees": paid_fees,
            "pending_fees": pending_fees,
            "due_date": "2026-07-15",
            "status": status,
            "transactions": txns
        }
        
    with open("mock_data/fees.json", "w", encoding="utf-8") as f:
        json.dump(fees_data, f, indent=2)

    # --- 4. Homework Data ---
    homework_data = {}
    
    # We define standard homework lists and assign them based on the student's status.
    for sid, name in zip(student_ids, student_names):
        # Homework due dates: some due tomorrow (July 4th), some in future, some past.
        # Since current_date = 2026-07-03, due tomorrow is 2026-07-04
        hw_list = [
            {
                "id": "HW401",
                "subject": "Mathematics",
                "title": "Trigonometric Identites",
                "due_date": "2026-07-04",
                "status": random.choice(["Pending", "Completed"]),
                "description": "Solve questions 1-15 in Chapter 8."
            },
            {
                "id": "HW402",
                "subject": "Science",
                "title": "Chemical Reactions Experiment Report",
                "due_date": "2026-07-04",
                "status": random.choice(["Pending", "Pending", "Completed"]),
                "description": "Submit a 2-page report detailing observations of acid-base titration."
            },
            {
                "id": "HW403",
                "subject": "English",
                "title": "Essay on Julius Caesar",
                "due_date": "2026-07-06",
                "status": "Pending",
                "description": "Write a 500-word analysis of Marcus Brutus' character."
            },
            {
                "id": "HW404",
                "subject": "Computer Science",
                "title": "Python Loops Homework",
                "due_date": "2026-07-02",
                "status": "Completed",
                "description": "Implement a script to calculate fibonacci sequence."
            }
        ]
        
        homework_data[sid] = {
            "student_name": name,
            "class": student_class_map[sid],
            "homework_list": hw_list
        }
        
    with open("mock_data/homework.json", "w", encoding="utf-8") as f:
        json.dump(homework_data, f, indent=2)

    # --- 5. Timetable Data ---
    # Standard class schedules for 10-A and 10-B
    timetable_data = {
        "10-A": {
            "Monday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Mathematics", "teacher": "Mr. Sharma"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Science", "teacher": "Mrs. Verma"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Computer Science", "teacher": "Ms. Roy"}
            ],
            "Tuesday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Science", "teacher": "Mrs. Verma"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Mathematics", "teacher": "Mr. Sharma"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Library/Sports", "teacher": "Mr. Patil"}
            ],
            "Wednesday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Mathematics", "teacher": "Mr. Sharma"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Science", "teacher": "Mrs. Verma"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Computer Science", "teacher": "Ms. Roy"}
            ],
            "Thursday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Science", "teacher": "Mrs. Verma"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Mathematics", "teacher": "Mr. Sharma"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Art & Craft", "teacher": "Ms. D'Souza"}
            ],
            "Friday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Mathematics", "teacher": "Mr. Sharma"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Science", "teacher": "Mrs. Verma"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Computer Science", "teacher": "Ms. Roy"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Social Studies", "teacher": "Mr. Dwivedi"}
            ]
        },
        "10-B": {
            "Monday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Science", "teacher": "Dr. Joseph"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Mathematics", "teacher": "Ms. Deshpande"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Computer Science", "teacher": "Ms. Roy"}
            ],
            "Tuesday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Mathematics", "teacher": "Ms. Deshpande"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Science", "teacher": "Dr. Joseph"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Library/Sports", "teacher": "Mr. Patil"}
            ],
            "Wednesday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Science", "teacher": "Dr. Joseph"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Mathematics", "teacher": "Ms. Deshpande"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Computer Science", "teacher": "Ms. Roy"}
            ],
            "Thursday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Mathematics", "teacher": "Ms. Deshpande"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Science", "teacher": "Dr. Joseph"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Social Studies", "teacher": "Mr. Dwivedi"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Art & Craft", "teacher": "Ms. D'Souza"}
            ],
            "Friday": [
                {"period": 1, "time": "08:30 - 09:15", "subject": "Science", "teacher": "Dr. Joseph"},
                {"period": 2, "time": "09:15 - 10:00", "subject": "Mathematics", "teacher": "Ms. Deshpande"},
                {"period": 3, "time": "10:15 - 11:00", "subject": "English", "teacher": "Mrs. Sen"},
                {"period": 4, "time": "11:00 - 11:45", "subject": "Computer Science", "teacher": "Ms. Roy"},
                {"period": 5, "time": "12:30 - 13:15", "subject": "Social Studies", "teacher": "Mr. Dwivedi"}
            ]
        }
    }
    
    with open("mock_data/timetable.json", "w", encoding="utf-8") as f:
        json.dump(timetable_data, f, indent=2)

    print("Successfully generated all mock data JSON files for 20 students.")

if __name__ == "__main__":
    generate_data()
