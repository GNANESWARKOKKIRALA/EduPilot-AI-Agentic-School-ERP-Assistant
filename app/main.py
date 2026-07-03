from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.database import engine, Base
from app.api import chat, history
from app.utils.logger import logger

# Run migrations / create database tables on application start
try:
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.critical(f"Failed to create database tables: {str(e)}")

app = FastAPI(
    title="EduPilot AI",
    description=(
        "Production-ready backend for the AI School ERP Assistant. "
        "Built using FastAPI, SQLAlchemy, and Llama 3.3 70B Versatile on Groq."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configurations to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(chat.router)
app.include_router(history.router)

@app.get("/", tags=["Diagnostics"])
def health_check():
    """
    Utility endpoint to verify that the backend API is online.
    """
    return {
        "app": "EduPilot AI ERP Assistant",
        "status": "Healthy",
        "engine": "Llama 3.3 70B",
        "api_docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
