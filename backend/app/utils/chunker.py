from collections.abc import Iterable

from app.services.transcript_service import TranscriptService


def chunk_words(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(words):
        chunks.append(" ".join(words[start : start + chunk_size]))
        start += step
    return chunks


def chunk_segments(
    segments: Iterable[dict],
    chunk_size: int = 1200,
    overlap: int = 250,
    metadata: dict | None = None,
) -> list[dict]:
    chunks = []
    current_words: list[str] = []
    current_segments: list[dict] = []
    current_start: float | None = None
    current_end: float | None = None
    base_metadata = metadata or {}

    for segment in segments:
        text = segment.get("text", "").strip()
        if not text:
            continue
        words = text.split()
        if current_start is None:
            current_start = float(segment.get("start", 0))
        current_end = float(segment.get("end", current_start or 0))
        current_words.extend(words)
        current_segments.append(
            {
                "start": float(segment.get("start", 0)),
                "end": float(segment.get("end", current_start or 0)),
                "text": text,
            }
        )

        while len(current_words) >= chunk_size:
            emitted = current_words[:chunk_size]
            timestamp = current_start if current_start is not None else 0
            chunks.append(
                {
                    "text": " ".join(emitted),
                    "start": current_start,
                    "end": current_end,
                    "timestamp": timestamp,
                    "timestamp_label": TranscriptService().timestamp_label(timestamp),
                    "segments": current_segments,
                    **base_metadata,
                }
            )
            current_words = current_words[chunk_size - overlap :]
            current_segments = current_segments[-1:] if current_segments else []
            current_start = current_segments[0]["start"] if current_segments else current_end

    if current_words:
        timestamp = current_start if current_start is not None else 0
        chunks.append(
            {
                "text": " ".join(current_words),
                "start": current_start,
                "end": current_end,
                "timestamp": timestamp,
                "timestamp_label": TranscriptService().timestamp_label(timestamp),
                "segments": current_segments,
                **base_metadata,
            }
        )
    return chunks
