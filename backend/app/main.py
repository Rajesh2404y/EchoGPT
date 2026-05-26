from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    audio_routes,
    chat_routes,
    notes_routes,
    quiz_routes,
    summary_routes,
    youtube_routes,
)
from app.core.config import get_settings
from app.core.logger import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title="EchoGPT API",
    description="Universal media knowledge assistant with Whisper, ChromaDB, and Ollama RAG.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(youtube_routes.router)
app.include_router(audio_routes.router)
app.include_router(chat_routes.router)
app.include_router(summary_routes.router)
app.include_router(notes_routes.router)
app.include_router(quiz_routes.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
