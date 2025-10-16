import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as main_router
from app.api.qa_endpoints import router as qa_router

app = FastAPI(
    title="ADOR - Augmented Document Reader",
    description="AI-powered financial document analysis with NER, Classification, Summarization, Topic Modelling, and Q&A",
    version="4.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(main_router)
app.include_router(qa_router)


@app.get("/")
async def root():
    return {
        "message": "ADOR API is running",
        "version": "4.0.0",
        "features": [
            "Entity Extraction",
            "Document Classification",
            "Summarization",
            "Topic Modelling",
            "Question Answering",
        ],
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "4.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
