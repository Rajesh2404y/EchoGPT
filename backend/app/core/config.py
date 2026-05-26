from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EchoGPT"
    environment: str = "development"
    api_prefix: str = ""
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    base_dir: Path = Path(__file__).resolve().parents[3]
    upload_dir: Path = Path("backend/uploads")
    transcript_dir: Path = Path("backend/transcripts")
    temp_dir: Path = Path("backend/temp")
    chroma_dir: Path = Path("backend/app/database/chromadb")
    whisper_cache_dir: Path = Path("backend/temp/cache/whisper")
    hf_cache_dir: Path = Path("backend/temp/cache/huggingface")

    whisper_model: str = "small"
    embedding_model: str = "BAAI/bge-small-en"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ollama_model: str = "qwen3:8b"
    ollama_host: str = "http://localhost:11434"
    ffmpeg_location: str | None = None

    chunk_size: int = 500
    chunk_overlap: int = 100
    retrieval_k: int = 8
    rerank_top_k: int = 5
    max_upload_mb: int = 250
    max_transcription_seconds: int = 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def path(self, value: Path) -> Path:
        return value if value.is_absolute() else self.base_dir / value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    for directory in (
        settings.upload_dir,
        settings.transcript_dir,
        settings.temp_dir,
        settings.chroma_dir,
        settings.whisper_cache_dir,
        settings.hf_cache_dir,
    ):
        settings.path(directory).mkdir(parents=True, exist_ok=True)
    return settings
