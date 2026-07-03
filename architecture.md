# Agentic Execution Architecture Flow

This document details the internal design of EduPilot AI's stateless agentic execution loop. The pipeline utilizes Llama 3.3 70B Versatile on Groq to orchestrate user query routing, database extraction, and context synthesis.

## 🏗️ Architecture Design Flow

Below is the step-by-step flowchart of the agentic lifecycle:

```
                  +--------------------------------+
                  |      Streamlit Frontend        |
                  +--------------------------------+
                                  |
                                  | POST /chat
                                  v
                  +--------------------------------+
                  |        FastAPI Backend         |
                  +--------------------------------+
                                  |
                                  | ChatService
                                  v
                  +--------------------------------+
                  |         Agent Planner          | <---> SQLite (Conversation History Memory)
                  +--------------------------------+
                                  |
                                  | Selected intents, entities, and tools JSON
                                  v
                  +--------------------------------+
                  |         Agent Executor         |
                  +--------------------------------+
                                  |
            +---------------------+---------------------+
            |                     |                     |
            v                     v                     v
    +---------------+     +---------------+     +---------------+
    |  Marks Tool   |     | AttendanceTool|     |   Fees Tool   |  ... (Other ERP Tools)
    +---------------+     +---------------+     +---------------+
            |                     |                     |
            +---------------------+---------------------+
                                  |
                                  | Aggregated JSON payload data
                                  v
                  +--------------------------------+
                  |         Reasoning Agent        | <---> Llama 3.3 Summary Synthesis
                  +--------------------------------+
                                  |
                                  | Save log & chat logs to SQLite database
                                  v
                  +--------------------------------+
                  |         Final Response         |
                  +--------------------------------+
```

---

## ⚙️ Component Explanations

### 1. Web Frontend (Streamlit)
The interface takes user queries, active student profiles, and (optionally) Groq API keys, executing POST calls to backend API `/chat` and rendering streamed typing responses.

### 2. Backend Gateway Router (FastAPI)
- Exposes REST paths.
- Validates the incoming body schema.
- Pre-validates if `student_id` is correct against active mock keys, raising a standard HTTP 404 response on failure.

### 3. Agent Planner
- Located in `app/agents/planner.py`.
- Formulates a system prompt linking the user query, Student ID, and the last 5 conversation context logs retrieved from `chat_history`.
- Fires a Groq API JSON completion requesting a detailed execution plan listing intents, extracted entities (like month or target weekday), and selected tool names.

### 4. Agent Executor
- Located in `app/agents/executor.py`.
- Audits the tool names selected by the planner.
- Directly routes and triggers independent tool modules, extracting parameters (like `homework_status`, `day_filter`, `exam_days_remaining`) from entities and merging all database payloads into a single structured output.

### 5. Reasoning Agent
- Located in `app/agents/reasoning.py`.
- Passes the aggregated database payload and memory context back to Llama 3.3 using the `SYSTEM_PROMPT`.
- Synthesizes a conversational natural language reply.
- Programmatically calculates a status flag (Critical, Warning, Pending, Paid, or Good) depending on student data metrics.

### 6. SQLite Database Logging
- Automatically inserts logs into:
  - `chat_history`: Conversation history logs for memory context.
  - `execution_logs`: Developer-facing performance audits, token counts, and elapsed latency meters.
