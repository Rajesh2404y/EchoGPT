import json
from json import JSONDecodeError
from pathlib import Path

from fastapi import HTTPException

from app.core.config import get_settings
from app.utils.cleaner import clean_transcript


class TranscriptService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def timestamp_label(self, seconds: float | None) -> str:
        total_seconds = int(seconds or 0)
        minutes, second = divmod(total_seconds, 60)
        hour, minute = divmod(minutes, 60)
        if hour:
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        return f"{minute:02d}:{second:02d}"

    def normalize(self, transcription: dict) -> dict:
        segments = []
        for segment in transcription.get("segments", []):
            text = clean_transcript(segment.get("text", ""))
            if text:
                start = float(segment.get("start", 0))
                end = float(segment.get("end", 0))
                segments.append(
                    {
                        "start": start,
                        "end": end,
                        "timestamp": start,
                        "timestamp_label": self.timestamp_label(start),
                        "text": text,
                    }
                )
        transcript = clean_transcript(" ".join(segment["text"] for segment in segments))
        return {"text": transcript, "segments": segments, "language": transcription.get("language")}

    def save(self, collection_id: str, payload: dict) -> Path:
        target = self.settings.path(self.settings.transcript_dir) / f"{collection_id}.json"
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target

    def load(self, collection_id: str) -> dict:
        if not collection_id:
            raise HTTPException(
                status_code=400,
                detail="Please process a YouTube URL or upload audio before generating content.",
            )
        target = self.settings.path(self.settings.transcript_dir) / f"{collection_id}.json"
        if not target.exists():
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Transcript not found for collection '{collection_id}'. "
                    "Please process the media again."
                ),
            )
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except JSONDecodeError as exc:
            raise HTTPException(
                status_code=500,
                detail="The saved transcript could not be read. Please process the media again.",
            ) from exc
