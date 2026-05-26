from pathlib import Path

from app.core.logger import get_logger
from app.services.chunk_service import ChunkService
from app.services.history_service import HistoryService
from app.services.timestamp_service import TimestampService
from app.services.transcript_service import TranscriptService
from app.services.vector_service import VectorService
from app.services.whisper_service import WhisperService
from app.utils.helpers import new_collection_id

logger = get_logger(__name__)


class MediaPipeline:
    def __init__(self) -> None:
        self.whisper = WhisperService()
        self.transcripts = TranscriptService()
        self.chunks = ChunkService()
        self.timestamps = TimestampService()
        self.history = HistoryService()

    async def process_audio(
        self, audio_path: Path, title: str, language: str | None = None, prefix: str = "media"
    ) -> dict:
        collection_id = new_collection_id(prefix)
        logger.info("Pipeline started: collection=%s title=%s", collection_id, title)
        logger.info("Transcription started: %s", audio_path)
        raw_transcript = await self.whisper.transcribe(audio_path, language)
        logger.info("Transcription finished: collection=%s", collection_id)
        transcript = self.transcripts.normalize(raw_transcript)
        chunk_payload = self.chunks.create_chunks(transcript)
        logger.info("Chunking finished: collection=%s chunks=%s", collection_id, len(chunk_payload))
        logger.info("Vector indexing started: collection=%s", collection_id)
        VectorService().upsert_chunks(collection_id, chunk_payload)
        logger.info("Vector indexing finished: collection=%s", collection_id)
        self.transcripts.save(
            collection_id,
            {
                "collection_id": collection_id,
                "title": title,
                "text": transcript["text"],
                "segments": transcript["segments"],
                "chunks": chunk_payload,
            },
        )
        self.history.add(collection_id, title, len(chunk_payload))
        logger.info("Pipeline finished: collection=%s", collection_id)
        return {
            "collection_id": collection_id,
            "title": title,
            "transcript": transcript["text"],
            "timestamps": self.timestamps.from_segments(transcript["segments"]),
            "chunks": len(chunk_payload),
        }
