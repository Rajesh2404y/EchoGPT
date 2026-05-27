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
        self,
        audio_path: Path,
        title: str,
        language: str | None = None,
        prefix: str = "media",
        video_id: str | None = None,
        source_url: str | None = None,
        max_seconds: int | None = None,
    ) -> dict:
        collection_id = new_collection_id(prefix)
        logger.info("Pipeline started: collection=%s title=%s", collection_id, title)
        logger.info("Transcription started: %s", audio_path)
        raw_transcript = await self.whisper.transcribe(audio_path, language, max_seconds=max_seconds)
        logger.info("Transcription finished: collection=%s", collection_id)
        transcript = self.transcripts.normalize(raw_transcript)
        transcribed_duration = transcript["segments"][-1]["end"] if transcript["segments"] else 0
        limit = None if max_seconds == -1 else (
            max_seconds if max_seconds is not None else self.whisper._transcription_limit()
        )
        is_truncated = bool(limit is not None and transcribed_duration >= limit - 1)
        source_metadata = {
            "collection_id": collection_id,
            "video_id": video_id or "",
            "source_url": source_url or "",
        }
        logger.info(
            "Chunking started: collection=%s words=%s chunk_size=%s overlap=%s",
            collection_id,
            len(transcript["text"].split()),
            self.chunks.settings.chunk_size,
            self.chunks.settings.chunk_overlap,
        )
        chunk_payload = self.chunks.create_chunks(transcript, source_metadata)
        logger.info("Chunking finished: collection=%s chunks=%s", collection_id, len(chunk_payload))
        VectorService().upsert_chunks(collection_id, chunk_payload)
        self.transcripts.save(
            collection_id,
            {
                "collection_id": collection_id,
                "title": title,
                "text": transcript["text"],
                "segments": transcript["segments"],
                "chunks": chunk_payload,
                "video_id": video_id,
                "source_url": source_url,
                "is_truncated": is_truncated,
                "transcription_limit_seconds": limit,
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
            "is_truncated": is_truncated,
            "processed_seconds": limit,
        }
