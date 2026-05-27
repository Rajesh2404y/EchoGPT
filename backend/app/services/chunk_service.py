from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.chunker import chunk_segments, chunk_words

logger = get_logger(__name__)


class ChunkService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def create_chunks(self, transcript: dict, metadata: dict | None = None) -> list[dict]:
        segments = transcript.get("segments") or []
        if segments:
            chunks = chunk_segments(
                segments,
                self.settings.chunk_size,
                self.settings.chunk_overlap,
                metadata,
            )
            logger.info(
                "Chunk processing finished: segments=%s chunks=%s",
                len(segments),
                len(chunks),
            )
            return chunks
        chunks = [
            {"text": chunk, "start": None, "end": None, **(metadata or {})}
            for chunk in chunk_words(
                transcript.get("text", ""), self.settings.chunk_size, self.settings.chunk_overlap
            )
        ]
        logger.info("Chunk processing finished: chunks=%s", len(chunks))
        return chunks
