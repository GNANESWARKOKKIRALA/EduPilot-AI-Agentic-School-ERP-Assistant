from fpdf import FPDF
import os

class APIDocPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(31, 111, 235)
        self.cell(0, 10, 'EduPilot AI - API Reference Manual', 0, 1, 'L')
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(100, 110, 120)
        self.cell(0, 5, 'Production REST API interface definitions, payload schemas, and client examples.', 0, 1, 'L')
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf():
    pdf = APIDocPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Section 1
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(35, 134, 54)
    pdf.cell(0, 8, '1. POST /chat - Submit Conversation Message', 0, 1, 'L')
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(33, 37, 41)
    pdf.multi_cell(0, 5, 'Description: Sends a natural language query for a specific student profile. Evaluates intents, executes planned ERP tools, compiles summaries, and logs metrics in SQLite.')
    pdf.ln(4)
    
    # Headers
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(210, 153, 34)
    pdf.cell(0, 6, 'Request Headers', 0, 1, 'L')
    
    # Table header
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(36, 41, 47)
    pdf.set_fill_color(246, 248, 250)
    pdf.cell(40, 6, 'Header Key', 1, 0, 'L', True)
    pdf.cell(25, 6, 'Type', 1, 0, 'L', True)
    pdf.cell(25, 6, 'Required', 1, 0, 'L', True)
    pdf.cell(90, 6, 'Description', 1, 1, 'L', True)
    
    # Table rows
    pdf.set_font('Helvetica', '', 8.5)
    pdf.cell(40, 6, 'Content-Type', 1, 0, 'L')
    pdf.cell(25, 6, 'string', 1, 0, 'L')
    pdf.cell(25, 6, 'Yes', 1, 0, 'L')
    pdf.cell(90, 6, 'application/json', 1, 1, 'L')
    
    pdf.cell(40, 6, 'X-Groq-API-Key', 1, 0, 'L')
    pdf.cell(25, 6, 'string', 1, 0, 'L')
    pdf.cell(25, 6, 'No', 1, 0, 'L')
    pdf.cell(90, 6, 'Optional Groq key to enable Llama 3.3 agent planning.', 1, 1, 'L')
    pdf.ln(4)
    
    # Request Body
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(210, 153, 34)
    pdf.cell(0, 6, 'Request Body JSON Payload', 0, 1, 'L')
    
    pdf.set_font('Courier', '', 8.5)
    pdf.set_text_color(13, 17, 23)
    pdf.set_fill_color(246, 248, 250)
    req_body = """{
  "student_id": "ST101",
  "message": "Show my midterm marks and check pending fees."
}"""
    pdf.multi_cell(0, 4.5, req_body, 1, 'L', True)
    pdf.ln(4)
    
    # Response Body
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(210, 153, 34)
    pdf.cell(0, 6, 'Response JSON Payload (200 OK)', 0, 1, 'L')
    
    pdf.set_font('Courier', '', 8.5)
    resp_body = """{
  "intent": "Multi-intent",
  "plan": [
    "Identify student ST101",
    "Load marks database",
    "Load fees database",
    "Calculate averages & outstanding dues",
    "Generate consolidated output"
  ],
  "tool": "Marks Tool, Fees Tool",
  "response": {
    "marks": {
      "student_name": "Aarav Mehta",
      "class": "10-A",
      "exams": {
        "Midterm": {
          "Mathematics": 88,
          "Science": 72
        }
      }
    },
    "fees": {
      "pending_fees": 6000,
      "status": "Pending"
    }
  },
  "summary": "You have a midterm average of 80%...",
  "status": "Pending",
  "execution_time": 1.12
}"""
    pdf.multi_cell(0, 4, resp_body, 1, 'L', True)
    
    pdf.add_page()
    
    # Section 2
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(35, 134, 54)
    pdf.cell(0, 8, '2. GET /chat/history - Retrieve Conversation Logs', 0, 1, 'L')
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(33, 37, 41)
    pdf.multi_cell(0, 5, 'Description: Fetches chronological conversation transcripts stored in SQLite.')
    pdf.ln(4)
    
    # Query Parameters
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(210, 153, 34)
    pdf.cell(0, 6, 'Query Parameters', 0, 1, 'L')
    
    # Table header
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(36, 41, 47)
    pdf.set_fill_color(246, 248, 250)
    pdf.cell(30, 6, 'Parameter', 1, 0, 'L', True)
    pdf.cell(20, 6, 'Type', 1, 0, 'L', True)
    pdf.cell(20, 6, 'Required', 1, 0, 'L', True)
    pdf.cell(20, 6, 'Default', 1, 0, 'L', True)
    pdf.cell(90, 6, 'Description', 1, 1, 'L', True)
    
    # Table rows
    pdf.set_font('Helvetica', '', 8.5)
    pdf.cell(30, 6, 'student_id', 1, 0, 'L')
    pdf.cell(20, 6, 'string', 1, 0, 'L')
    pdf.cell(20, 6, 'No', 1, 0, 'L')
    pdf.cell(20, 6, 'None', 1, 0, 'L')
    pdf.cell(90, 6, 'Filter results specifically by student ID.', 1, 1, 'L')
    
    pdf.cell(30, 6, 'limit', 1, 0, 'L')
    pdf.cell(20, 6, 'int', 1, 0, 'L')
    pdf.cell(20, 6, 'No', 1, 0, 'L')
    pdf.cell(20, 6, '50', 1, 0, 'L')
    pdf.cell(90, 6, 'Cap returned log list size (max 100).', 1, 1, 'L')
    pdf.ln(4)
    
    # Response
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(210, 153, 34)
    pdf.cell(0, 6, 'Response JSON Payload (200 OK)', 0, 1, 'L')
    
    pdf.set_font('Courier', '', 8.5)
    pdf.set_text_color(13, 17, 23)
    history_resp = """[
  {
    "id": 1,
    "student_id": "ST101",
    "query": "Show my midterm marks.",
    "intent": "Marks",
    "tool_used": "Marks Tool",
    "response": {
      "summary": "Your midterm average is..."
    },
    "timestamp": "2026-07-03T09:20:30Z",
    "execution_time": 0.85
  }
]"""
    pdf.multi_cell(0, 4.5, history_resp, 1, 'L', True)
    pdf.ln(4)
    
    # Section 3
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(35, 134, 54)
    pdf.cell(0, 8, '3. cURL CLI Invocation Example', 0, 1, 'L')
    
    pdf.set_font('Courier', '', 8.5)
    pdf.set_text_color(13, 17, 23)
    curl_ex = """curl -X POST "http://127.0.0.1:8000/chat" \\
     -H "Content-Type: application/json" \\
     -H "X-Groq-API-Key: your_key_here" \\
     -d '{"student_id": "ST101", "message": "Show homework due tomorrow."}'"""
    pdf.multi_cell(0, 5, curl_ex, 1, 'L', True)
    
    # Output PDF
    os.makedirs("docs", exist_ok=True)
    pdf.output("docs/api_docs.pdf")
    print("PDF successfully generated using fpdf2 at docs/api_docs.pdf")

if __name__ == "__main__":
    generate_pdf()
