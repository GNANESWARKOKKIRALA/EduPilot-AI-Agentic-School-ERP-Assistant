import json
from groq import Groq
from app.config import settings
from app.utils.logger import logger

class LLMService:
    """
    Service layer interacting with the Groq Cloud API.
    Provides standard text generation and structured JSON mode generation.
    Includes local fallback modes for setup and testing when API keys are mock or invalid.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.is_mock_key = not self.api_key or self.api_key.startswith("gsk_mock")
        
        # Instantiate Groq client if the key is not mock
        if not self.is_mock_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Using mock/invalid Groq API key. Local fallback engine will handle requests.")

    def get_completion(self, system_message: str, user_message: str, temperature: float = 0.1) -> tuple[str, int]:
        """
        Sends a standard chat request to the LLM. Fallback is activated if API keys are missing/invalid.
        Returns a tuple: (content_string, total_tokens_used).
        """
        if self.is_mock_key or not self.client:
            logger.info("Executing local fallback summary generator.")
            return self._local_fallback_reasoning(user_message), 0

        logger.info(f"Querying Groq text completion using model: {self.model}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature
            )
            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0
            logger.info(f"Successfully received response. Tokens used: {tokens}")
            return content, tokens
        except Exception as e:
            logger.error(f"Groq API text completion error: {str(e)}")
            if "invalid api key" in str(e).lower() or "401" in str(e):
                logger.warning("API key failed. Recovering using local fallback summary generator.")
                return self._local_fallback_reasoning(user_message), 0
            raise

    def get_json_completion(self, user_message: str, temperature: float = 0.1) -> tuple[dict, int]:
        """
        Sends a request to the LLM forcing JSON output format. Fallback is activated on mock key.
        Returns a tuple: (parsed_json_dict, total_tokens_used).
        """
        if self.is_mock_key or not self.client:
            logger.info("Executing local fallback planner parser.")
            return self._local_fallback_plan(user_message), 0

        logger.info(f"Querying Groq JSON completion using model: {self.model}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=temperature
            )
            content = response.choices[0].message.content or "{}"
            tokens = response.usage.total_tokens if response.usage else 0
            
            try:
                parsed_json = json.loads(content)
                logger.info(f"Successfully received and parsed JSON response. Tokens used: {tokens}")
                return parsed_json, tokens
            except json.JSONDecodeError as jde:
                logger.error(f"Failed to parse JSON content from Groq response: {content}. Error: {str(jde)}")
                raise ValueError("LLM did not return valid JSON despite JSON mode.")
        except Exception as e:
            logger.error(f"Groq API JSON completion error: {str(e)}")
            if "invalid api key" in str(e).lower() or "401" in str(e):
                logger.warning("API key failed. Recovering using local fallback planner parser.")
                return self._local_fallback_plan(user_message), 0
            raise

    def _local_fallback_plan(self, user_message: str) -> dict:
        """
        Rule-based NLP execution planner to serve query intents in case of missing Groq keys.
        """
        # Extract the user's raw query from the formatted planner prompt template
        raw_prompt = user_message.lower()
        msg = raw_prompt
        if 'user query: "' in raw_prompt:
            try:
                msg = raw_prompt.split('user query: "')[1].split('"\n')[0]
            except Exception:
                msg = raw_prompt
        
        tools = []
        intents = []
        entities = {"month": None, "subject": None, "due_date": None, "day": None}
        
        # Match weekdays
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        for day in days:
            if day in msg:
                entities["day"] = day.capitalize()
                
        # Parse queries and identify target tools
        if any(k in msg for k in ["attendance", "attendence", "absent", "present", "miss", "class"]):
            tools.append("attendance")
            intents.append("Attendance")
        if any(k in msg for k in ["marks", "grade", "score", "exam", "midterm", "study", "planner"]):
            tools.append("marks")
            intents.append("Marks")
        if any(k in msg for k in ["fee", "pay", "due", "transaction", "unpaid", "pending"]):
            tools.append("fees")
            intents.append("Fees")
        if any(k in msg for k in ["homework", "assignment", "task"]):
            tools.append("homework")
            intents.append("Homework")
            if "tomorrow" in msg:
                entities["due_date"] = "tomorrow"
        if any(k in msg for k in ["timetable", "schedule", "period", "timing"]):
            tools.append("timetable")
            intents.append("Timetable")
        if any(k in msg for k in ["performance", "progress", "parent", "standing", "report"]):
            tools.append("performance")
            intents.append("Performance")
        if any(k in msg for k in ["recommend", "suggest", "tip", "weak", "advice"]):
            tools.append("recommendation")
            intents.append("Recommendation")
            
        if not tools:
            # Look for general greetings
            if any(k in msg for k in ["hi", "hello", "hey", "greeting"]):
                return {
                    "intent": "Greeting",
                    "confidence": 1.0,
                    "entities": {},
                    "tools": [],
                    "plan": ["Process greeting", "Offer help with attendance, marks, fees, homework, timetable"]
                }
            # Default to performance summary if unclear
            tools = ["performance"]
            intents = ["Performance"]
            
        intent = "Multi-intent" if len(tools) > 1 else intents[0]
        
        plan_steps = ["Identify student ST101 and load profile meta"]
        for t in tools:
            plan_steps.append(f"Load {t}.json database records")
            plan_steps.append(f"Execute {t.capitalize()} Tool calculations")
        plan_steps.append("Consolidate raw payloads and format output")
        
        return {
            "intent": intent,
            "confidence": 0.95,
            "entities": entities,
            "tools": tools,
            "plan": plan_steps
        }

    def _local_fallback_reasoning(self, user_message: str) -> str:
        """
        Rule-based response composer that aggregates raw tool payloads into text summaries.
        """
        try:
            # Retrieve the serialized JSON payload embedded in the user prompt
            if "Tool Output Payload:" in user_message:
                payload_part = user_message.split("Tool Output Payload:\n")[1].split("\n\n")[0]
                tool_outputs = json.loads(payload_part)
            else:
                tool_outputs = {}
        except Exception:
            tool_outputs = {}
            
        if not tool_outputs:
            if any(k in user_message.lower() for k in ["hi", "hello", "hey"]):
                return (
                    "Hello! I am **EduPilot AI**, your intelligent school ERP assistant.\n\n"
                    "How can I help you today? You can ask me questions like:\n"
                    "- *\"Show my attendance this month and check pending fees.\"* (Multi-tool)\n"
                    "- *\"Which subject did I score highest in?\"* (Midterm marks)\n"
                    "- *\"Do I have homework due tomorrow?\"*\n"
                    "- *\"What is my timetable on Monday?\"*\n"
                    "- *\"Provide some recommendations.\"*"
                )
            return "I am online and ready. Please ask an ERP related question about attendance, marks, fees, homework, or timetable."

        summaries = []
        student_name = "Student"
        
        # Extract student name
        for key in tool_outputs:
            if isinstance(tool_outputs[key], dict) and "student_name" in tool_outputs[key]:
                student_name = tool_outputs[key]["student_name"]
                break
                
        summaries.append(f"Hello **{student_name}**! Here is the data retrieved from the EduPilot ERP system:")
        
        if "attendance" in tool_outputs:
            att = tool_outputs["attendance"]
            pct = att.get("attendance_percentage", 0.0)
            pres = att.get("present", 0)
            abs_val = att.get("absent", 0)
            proj = att.get("projection", {})
            
            summaries.append(
                f"\n### 📅 Attendance status\n"
                f"- **Attendance Percentage:** **{pct}%**\n"
                f"- **Present Days:** {pres} | **Absent Days:** {abs_val}\n"
                f"- **Insight:** {proj.get('explanation', '')}"
            )
            
        if "marks" in tool_outputs:
            m = tool_outputs["marks"]
            analysis = m.get("analysis", {})
            exams = m.get("exams", {})
            midterm = exams.get("Midterm", {})
            avg = analysis.get("average_marks", 0.0)
            weak = ", ".join(analysis.get("weak_subjects", []))
            strong = ", ".join(analysis.get("strong_subjects", []))
            
            scores_formatted = ", ".join([f"{subj}: **{score}%**" for subj, score in midterm.items()])
            
            summaries.append(
                f"\n### 📝 Exam Marks (Midterm Results)\n"
                f"- **Subject Scores:** {scores_formatted}\n"
                f"- **Average Marks:** **{avg}%**\n"
                f"- **Strongest Subject:** *{analysis.get('highest_subject', 'N/A')}* ({analysis.get('highest_score')}%)\n"
                f"- **Weakest Subject:** *{analysis.get('lowest_subject', 'N/A')}* ({analysis.get('lowest_score')}%)"
            )
            
            if weak:
                summaries.append(f"- **Study Advice:** Since you are struggling in **{weak}**, focus study blocks on these.")
                
            # Add study planner detail if selected
            planner = m.get("study_planner", {})
            if planner and "schedule" in planner:
                summaries.append(f"\n#### 🗓️ Personal Exam Study Schedule:")
                for subj, s_item in planner["schedule"].items():
                    summaries.append(
                        f"  * **{subj}** ({s_item['priority']} Priority): Study **{s_item['daily_study_hours_allocated']} hrs/day** "
                        f"(Total allocated: {s_item['total_study_hours_allocated']} hrs)"
                    )
                
        if "fees" in tool_outputs:
            fees = tool_outputs["fees"]
            pending = fees.get("pending_fees", 0)
            status = fees.get("status", "Pending")
            due = fees.get("due_date", "")
            
            if pending > 0:
                summaries.append(
                    f"\n### 💳 Fees Ledger\n"
                    f"- **Pending Dues:** **{pending} INR**\n"
                    f"- **Status:** ⚠️ {status}\n"
                    f"- **Payment Deadline:** {due}"
                )
            else:
                summaries.append(
                    f"\n### 💳 Fees Ledger\n"
                    f"- **Status:** ✅ Fully Paid (No outstanding dues)."
                )
                
        if "homework" in tool_outputs:
            hw = tool_outputs["homework"]
            pending_count = hw.get("pending_count", 0)
            due_tomorrow = hw.get("due_tomorrow_assignments", [])
            
            summaries.append(
                f"\n### 📝 Homework & Tasks\n"
                f"- **Pending Assignments:** **{pending_count}**"
            )
            
            if due_tomorrow:
                summaries.append(f"- **Due Tomorrow:**")
                for item in due_tomorrow:
                    summaries.append(f"  * **{item['subject']}**: *\"{item['title']}\"* - {item['description']}")
            else:
                summaries.append("- **Due Tomorrow:** None (You are all caught up!)")
                
        if "timetable" in tool_outputs:
            tt = tool_outputs["timetable"]
            cls = tt.get("class", "")
            timetable_map = tt.get("timetable", {})
            
            summaries.append(f"\n### 📅 Class Timetable (Class {cls})")
            for day, periods in timetable_map.items():
                summaries.append(f"- **{day}:**")
                for p in periods:
                    summaries.append(f"  * Period {p['period']} ({p['time']}): **{p['subject']}** with {p['teacher']}")
                    
        if "performance" in tool_outputs:
            perf = tool_outputs["performance"]
            report = perf.get("parent_report", {})
            summaries.append(
                f"\n### 📊 Overall Academic Standing\n"
                f"- **Current standing:** **{report.get('overall_performance', 'N/A')}**\n"
                f"- **Attendance summary:** {report.get('attendance_summary')}\n"
                f"- **Marks summary:** {report.get('marks_summary')}\n"
                f"- **Homework summary:** {report.get('homework_summary')}\n"
                f"- **Fee Status:** {report.get('fee_status')}"
            )
            
        if "recommendation" in tool_outputs:
            rec = tool_outputs["recommendation"]
            recs = rec.get("recommendations", [])
            summaries.append(f"\n### 💡 Smart Personal Recommendations")
            for r in recs:
                severity_emoji = "🚨" if r["severity"] == "High" else ("⚠️" if r["severity"] == "Medium" else "✅")
                summaries.append(f"- {severity_emoji} **{r['category']}**: {r['message']}")

        summaries.append("\n\n*(Heuristic analysis offline. Please enter a valid GROQ_API_KEY in the .env configuration file to activate Llama 3.3 70B Versatile.)*")
        
        return "\n".join(summaries)
