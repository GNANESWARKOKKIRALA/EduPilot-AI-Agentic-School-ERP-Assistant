import os
import json
import requests
import streamlit as st
import time
from datetime import datetime

# Streamlit Page Configurations
st.set_page_config(
    page_title="EduPilot AI – Agentic School ERP Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Professional Custom CSS styling for premium SaaS-like look
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Global style overrides */
    .stApp {
        background-color: #0b0d13;
        color: #e6edf3;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sidebar redesign */
    [data-testid="stSidebar"] {
        background-color: #07090e;
        border-right: 2px solid #21262d;
    }
    
    /* Glowing brand headers */
    .brand-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1f6feb 0%, #8957e5 50%, #f62d8e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .brand-subtitle {
        font-size: 0.9rem;
        color: #8b949e;
        margin-top: 0px;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }
    
    /* Premium card design for student profile */
    .profile-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 15px;
        margin-top: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .profile-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #58a6ff;
        margin-bottom: 8px;
    }
    .profile-meta {
        font-size: 0.85rem;
        color: #8b949e;
        margin: 4px 0;
    }
    
    /* Custom status badges */
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 6px;
    }
    .badge-good {
        background-color: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.12);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.12);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }
    
    /* Status indicators */
    .status-online {
        color: #39d353;
        font-weight: 600;
    }
    .status-offline {
        color: #f85149;
        font-weight: 600;
    }
    
    /* Custom Chat Message Bubbles styling */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        margin-bottom: 14px;
        padding: 16px;
        transition: all 0.2s ease-in-out;
    }
    
    /* Assistant bubble design (Charcoal and purple left border) */
    div[data-testid="stChatMessage"][data-testid$="assistant"] {
        background-color: #141923 !important;
        border-left: 5px solid #8957e5 !important;
        border-top: 1px solid #30363d !important;
        border-bottom: 1px solid #30363d !important;
        border-right: 1px solid #30363d !important;
    }
    div[data-testid="stChatMessage"][data-testid$="assistant"]:hover {
        border-color: #8957e5;
        box-shadow: 0 6px 16px rgba(137, 87, 229, 0.12);
    }
    
    /* User bubble design (Deep sapphire gradient) */
    div[data-testid="stChatMessage"][data-testid$="user"] {
        background: linear-gradient(135deg, #0f1c30 0%, #172c47 100%) !important;
        border: 1px solid #23446b !important;
    }
    div[data-testid="stChatMessage"][data-testid$="user"]:hover {
        border-color: #388bfd;
        box-shadow: 0 6px 16px rgba(56, 139, 253, 0.15);
    }
    
    /* Custom input field styling */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
    }
    
    /* Custom styling for Expanders to look like console logs */
    .streamlit-expanderHeader {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #58a6ff !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        background-color: #090d13 !important;
        border: 1px solid #30363d !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        font-family: 'JetBrains Mono', monospace;
        padding: 15px !important;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Constants
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def check_backend_status() -> bool:
    """Checks whether the FastAPI backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def load_student_list() -> dict[str, dict]:
    """Loads student database metadata to display rich profile cards."""
    meta_path = "mock_data/attendance.json"
    marks_path = "mock_data/marks.json"
    
    default_students = {
        f"ST{i}": {"name": f"Student {i}", "class": "10-A", "attendance": 90.0, "avg_marks": 75.0} 
        for i in range(101, 121)
    }
    
    if os.path.exists(meta_path) and os.path.exists(marks_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f1, open(marks_path, "r", encoding="utf-8") as f2:
                att_data = json.load(f1)
                marks_data = json.load(f2)
                
                resolved = {}
                for sid in att_data:
                    m_rec = marks_data.get(sid, {})
                    midterm = m_rec.get("exams", {}).get("Midterm", {})
                    scores = list(midterm.values())
                    avg = round(sum(scores) / len(scores), 1) if scores else 0.0
                    
                    resolved[sid] = {
                        "name": att_data[sid]["student_name"],
                        "class": att_data[sid]["class"],
                        "attendance": att_data[sid]["summary"]["percentage"],
                        "avg_marks": avg
                    }
                return resolved
        except Exception:
            return default_students
    return default_students

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("<div class='brand-title'>EduPilot AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>School ERP Assistant • Premium</div>", unsafe_allow_html=True)
    
    # 1. API Health Check
    is_online = check_backend_status()
    if is_online:
        st.markdown("API Status: <span class='status-online'>● Online</span>", unsafe_allow_html=True)
    else:
        st.markdown("API Status: <span class='status-offline'>● Offline</span>", unsafe_allow_html=True)
        st.warning("FastAPI Backend is currently unreachable.")
        
    st.markdown("---")
    
    # 2. Dynamic Groq Key Input
    groq_key = st.text_input(
        "Enter Groq API Key (Optional)", 
        type="password",
        placeholder="gsk_...",
        help="Input your Groq API Key to enable Llama 3.3. If blank, EduPilot operates on offline mock fallback mode."
    )
    
    st.markdown("---")
    
    # 3. Student ID Selector
    student_map = load_student_list()
    selected_sid = st.selectbox(
        "Select Active Student Profile",
        options=list(student_map.keys()),
        format_func=lambda sid: f"{sid} - {student_map[sid]['name']}"
    )
    
    active_sid = selected_sid.strip().upper()
    
    # 4. Premium Visual Student Profile Card
    if active_sid in student_map:
        profile = student_map[active_sid]
        att = profile.get("attendance", 0.0)
        avg = profile.get("avg_marks", 0.0)
        
        # Inferred academic standing
        if att >= 88.0 and avg >= 80.0:
            badge_class = "badge-good"
            badge_lbl = "Good Standing"
        elif att < 75.0 or avg < 55.0:
            badge_class = "badge-danger"
            badge_lbl = "Critical Attention"
        else:
            badge_class = "badge-warning"
            badge_lbl = "Academic Warning"
            
        st.markdown(
            f"""
            <div class='profile-card'>
                <div class='profile-name'>{profile['name']}</div>
                <div class='profile-meta'>🆔 <b>Student ID:</b> {active_sid}</div>
                <div class='profile-meta'>🏫 <b>Classroom:</b> Grade {profile['class']}</div>
                <div class='profile-meta'>📅 <b>Attendance:</b> {att}%</div>
                <div class='profile-meta'>📈 <b>Grade Avg:</b> {avg}%</div>
                <div>
                    <span class='status-badge {badge_class}'>{badge_lbl}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("---")
    
    # 5. Clear conversation history action
    if st.button("🗑️ Reset Chat History", use_container_width=True):
        st.session_state.messages = []
        st.success("Conversation history cleared.")
        st.rerun()

# --- MAIN APP LAYOUT ---
st.markdown("## 🎓 EduPilot ERP Dashboard")

# Initialize conversation message history state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fetch chat logs from SQLite to initialize conversation history on student change
if "last_sid" not in st.session_state or st.session_state.last_sid != active_sid:
    st.session_state.last_sid = active_sid
    st.session_state.messages = []
    if is_online:
        try:
            res = requests.get(f"{BACKEND_URL}/chat/history?student_id={active_sid}&limit=10")
            if res.status_code == 200:
                history_data = res.json()
                history_data.reverse()
                for item in history_data:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": item["query"]
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": item["response"].get("summary", ""),
                        "meta": item["response"]
                    })
        except Exception as e:
            st.error(f"Failed to load database history: {str(e)}")

# Welcome dashboard if conversation is empty
if not st.session_state.messages:
    st.markdown("#### Hello! I am EduPilot AI, your school ERP Assistant. How can I help you today?")
    st.markdown("<br/>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("📅 Attendance Logs", use_container_width=True, key="welcome_att"):
            st.session_state.clicked_prompt = "Show my attendance stats."
            st.rerun()
    with cols[1]:
        if st.button("📝 Exams & Marks", use_container_width=True, key="welcome_marks"):
            st.session_state.clicked_prompt = "Show my midterm marks."
            st.rerun()
    with cols[2]:
        if st.button("💳 Tuition Fees", use_container_width=True, key="welcome_fees"):
            st.session_state.clicked_prompt = "Do I have pending fees?"
            st.rerun()
    with cols[3]:
        if st.button("🔔 Homework Tasks", use_container_width=True, key="welcome_hw"):
            st.session_state.clicked_prompt = "Do I have homework due tomorrow?"
            st.rerun()
            
    st.markdown("<br/><br/>", unsafe_allow_html=True)

# Display historical messages in chat interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        # Display plan and tools if they exist in the metadata
        if msg["role"] == "assistant" and "meta" in msg:
            meta = msg["meta"]
            
            # Format UI tags
            cols = st.columns([1, 1, 1, 1])
            with cols[0]:
                st.caption(f"🎯 **Intent:** `{meta.get('intent', 'N/A')}`")
            with cols[1]:
                st.caption(f"🛠️ **Tool:** `{meta.get('tool', 'N/A')}`")
            with cols[2]:
                status_val = meta.get('status', 'Good')
                color_emoji = {"Good": "🟢", "Paid": "🟢", "Warning": "🟡", "Pending": "🟡", "Critical": "🔴"}.get(status_val, "⚪")
                st.caption(f"📊 **Status:** {color_emoji} `{status_val}`")
            with cols[3]:
                st.caption(f"⚡ **Latency:** `{meta.get('execution_time', 0.0)}s`")
                
            # Collapsibles for detailed developer insight (Removed Raw ERP Payload)
            with st.expander("🔍 Agent Reasoning Chain"):
                st.markdown("**Execution Plan Steps:**")
                for step in meta.get("plan", []):
                    st.markdown(f"- {step}")

# Display quick suggestions above the input bar if history exists
if st.session_state.messages:
    st.markdown("---")
    cols_suggest = st.columns(4)
    with cols_suggest[0]:
        if st.button("📅 Check Attendance", key="suggest_att", use_container_width=True):
            st.session_state.clicked_prompt = "Show my attendance stats."
            st.rerun()
    with cols_suggest[1]:
        if st.button("📝 Midterm Grades", key="suggest_marks", use_container_width=True):
            st.session_state.clicked_prompt = "Show my midterm marks."
            st.rerun()
    with cols_suggest[2]:
        if st.button("💳 Pending Dues", key="suggest_fees", use_container_width=True):
            st.session_state.clicked_prompt = "Do I have pending fees?"
            st.rerun()
    with cols_suggest[3]:
        if st.button("🔔 Homework Tasks", key="suggest_hw", use_container_width=True):
            st.session_state.clicked_prompt = "Do I have homework due tomorrow?"
            st.rerun()

# Capture search bar input
chat_input_val = st.chat_input("Ask about attendance, marks, pending fees, homework due tomorrow, timetable...")
user_query = None

# Prioritize suggestion clicks over typed input
if "clicked_prompt" in st.session_state and st.session_state.clicked_prompt:
    user_query = st.session_state.clicked_prompt
    st.session_state.clicked_prompt = None
elif chat_input_val:
    user_query = chat_input_val

# --- HANDLER FOR NEW USER QUERIES ---
if user_query:
    # Render user query bubble
    with st.chat_message("user"):
        st.write(user_query)
        
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Check backend is running
    if not is_online:
        with st.chat_message("assistant"):
            st.error("Cannot connect to EduPilot ERP Backend API. Please check your server connection.")
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Cannot connect to EduPilot ERP Backend API. Please check your server connection."
        })
    else:
        # Agent execution block
        with st.chat_message("assistant"):
            with st.spinner("EduPilot AI is planning and querying ERP tools..."):
                try:
                    payload = {
                        "student_id": active_sid,
                        "message": user_query
                    }
                    headers = {}
                    if groq_key:
                        headers["X-Groq-API-Key"] = groq_key
                        
                    response = requests.post(f"{BACKEND_URL}/chat", json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Render final summary with real-time typewriter effect
                        def stream_summary():
                            for word in data["summary"].split(" "):
                                yield word + " "
                                time.sleep(0.015)
                        st.write_stream(stream_summary())
                        
                        # Render status, intents, execution time
                        cols = st.columns([1, 1, 1, 1])
                        with cols[0]:
                            st.caption(f"🎯 **Intent:** `{data.get('intent', 'N/A')}`")
                        with cols[1]:
                            st.caption(f"🛠️ **Tool:** `{data.get('tool', 'N/A')}`")
                        with cols[2]:
                            status_val = data.get('status', 'Good')
                            color_emoji = {"Good": "🟢", "Paid": "🟢", "Warning": "🟡", "Pending": "🟡", "Critical": "🔴"}.get(status_val, "⚪")
                            st.caption(f"📊 **Status:** {color_emoji} `{data.get('status', 'Good')}`")
                        with cols[3]:
                            st.caption(f"⚡ **Latency:** `{data.get('execution_time', 0.0)}s`")
                            
                        # Collapsibles for detailed developer insight (Removed Raw ERP Payload)
                        with st.expander("🔍 Agent Reasoning Chain"):
                            st.markdown("**Execution Plan Steps:**")
                            for step in data.get("plan", []):
                                st.markdown(f"- {step}")
                            
                        # Save response to memory state
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["summary"],
                            "meta": data
                        })
                        st.rerun()  # Rerun to render suggestions properly and clear prompt states
                        
                    elif response.status_code == 404:
                        error_detail = response.json().get("detail", "Student ID not found.")
                        st.error(f"ERP Error (404): {error_detail}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"ERP Error (404): {error_detail}"
                        })
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"System Error: {response.text}"
                        })
                        
                except Exception as e:
                    st.error(f"Exception during request dispatch: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Exception occurred: {str(e)}"
                    })
