from app.core.config import get_settings
from app.utils.chunker import chunk_segments, chunk_words


class ChunkService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def create_chunks(self, transcript: dict) -> list[dict]:
        segments = transcript.get("segments") or []
        if segments:
            return chunk_segments(segments, self.settings.chunk_size, self.settings.chunk_overlap)
        return [
            {"text": chunk, "start": None, "end": None}
            for chunk in chunk_words(
                transcript.get("text", ""), self.settings.chunk_size, self.settings.chunk_overlap
            )
        ]
