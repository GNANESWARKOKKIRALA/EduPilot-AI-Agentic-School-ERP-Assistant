#!/bin/bash
# Start the FastAPI backend in the background
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Wait for backend initialization
sleep 3

# Start the Streamlit frontend in the foreground
PORT_NUM=${PORT:-8501}
python -m streamlit run frontend/streamlit_app.py --server.port $PORT_NUM --server.address 0.0.0.0
