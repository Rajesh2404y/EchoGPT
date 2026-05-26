from __future__ import annotations

import json
from pathlib import Path

from app.core.config import get_settings
from app.utils.helpers import utc_now_iso


class HistoryService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.path = self.settings.base_dir / "backend" / "transcripts" / "history.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, items: list[dict]) -> None:
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def _normalize(self, item: dict) -> dict | None:
        collection_id = item.get("collection_id") or item.get("id")
        if not collection_id:
            return None
        chat_id = item.get("chat_id") or item.get("id") or collection_id
        transcript_path = self.path.parent / f"{collection_id}.json"
        transcript = {}
        if transcript_path.exists():
            try:
                transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                transcript = {}
        text = transcript.get("text", "")
        summary = item.get("summary") or (text[:170] + "..." if len(text) > 170 else text)
        messages = [
            {
                "role": message.get("role", "assistant"),
                "content": message.get("content", ""),
                "timestamp": message.get("timestamp") or message.get("created_at"),
                "created_at": message.get("created_at") or message.get("timestamp"),
            }
            for message in item.get("messages", [])
            if message and message.get("content")
        ]
        last_message = messages[-1]["content"] if messages else summary
        return {
            "id": chat_id,
            "chat_id": chat_id,
            "collection_id": collection_id,
            "title": item.get("title") or transcript.get("title") or "Untitled media",
            "created_at": item.get("created_at") or "",
            "updated_at": item.get("updated_at") or item.get("created_at") or "",
            "chunks": item.get("chunks") or len(transcript.get("chunks", [])),
            "summary": summary or "Transcript ready for chat, summaries, notes, and quizzes.",
            "last_message": last_message or "No messages yet.",
            "type": item.get("type") or ("youtube" if collection_id.startswith("yt_") else "audio"),
            "messages": messages,
        }

    def add(self, collection_id: str, title: str, chunks: int) -> None:
        items = self._read()
        timestamp = utc_now_iso()
        items.insert(
            0,
            {
                "id": collection_id,
                "chat_id": collection_id,
                "collection_id": collection_id,
                "title": title,
                "created_at": timestamp,
                "updated_at": timestamp,
                "chunks": chunks,
                "summary": f"Processed media with {chunks} transcript chunk{'s' if chunks != 1 else ''}.",
                "type": "youtube" if collection_id.startswith("yt_") else "audio",
                "messages": [],
            },
        )
        self._write(items)

    def list(self) -> list[dict]:
        items = []
        for item in self._read():
            normalized = self._normalize(item)
            if normalized:
                normalized.pop("messages", None)
                items.append(normalized)
        return items

    def get(self, chat_id: str) -> dict | None:
        for item in self._read():
            if chat_id in {item.get("chat_id"), item.get("id"), item.get("collection_id")}:
                return self._normalize(item)
        return None

    def append_messages(self, collection_id: str | None, messages: list[dict]) -> None:
        if not collection_id or not messages:
            return
        timestamp = utc_now_iso()
        items = self._read()
        for item in items:
            if collection_id in {item.get("chat_id"), item.get("id"), item.get("collection_id")}:
                item.setdefault("messages", [])
                item.setdefault("chat_id", item.get("id") or collection_id)
                item["messages"].extend(
                    {
                        "role": message.get("role", "assistant"),
                        "content": message.get("content", ""),
                        "timestamp": message.get("timestamp") or message.get("created_at") or timestamp,
                        "created_at": message.get("created_at") or timestamp,
                    }
                    for message in messages
                    if message.get("content")
                )
                item["updated_at"] = timestamp
                self._write(items)
                return

    def increment_summary(self, collection_id: str | None) -> None:
        if not collection_id:
            return
        items = self._read()
        timestamp = utc_now_iso()
        for item in items:
            if collection_id in {item.get("chat_id"), item.get("id"), item.get("collection_id")}:
                item["summary_count"] = int(item.get("summary_count") or 0) + 1
                item["updated_at"] = timestamp
                self._write(items)
                return

    def append_generated_content(self, collection_id: str | None, kind: str, content: str) -> None:
        if not collection_id or not content:
            return
        timestamp = utc_now_iso()
        items = self._read()
        for item in items:
            if collection_id in {item.get("chat_id"), item.get("id"), item.get("collection_id")}:
                item.setdefault("generated", [])
                item["generated"].append(
                    {
                        "kind": kind,
                        "content": content,
                        "created_at": timestamp,
                    }
                )
                if kind == "summary":
                    item["summary_count"] = int(item.get("summary_count") or 0) + 1
                item["updated_at"] = timestamp
                self._write(items)
                return

    def stats(self) -> dict:
        items = [item for item in (self._normalize(raw) for raw in self._read()) if item]
        raw_items = self._read()
        return {
            "videos_processed": sum(1 for item in items if item.get("type") == "youtube"),
            "audio_files": sum(1 for item in items if item.get("type") == "audio"),
            "questions_asked": sum(
                1
                for item in items
                for message in item.get("messages", [])
                if message.get("role") == "user"
            ),
            "summaries_generated": sum(
                max(
                    int(raw.get("summary_count") or 0),
                    sum(1 for generated in raw.get("generated", []) if generated.get("kind") == "summary"),
                )
                for raw in raw_items
            ),
        }

    def delete(self, collection_id: str) -> None:
        items = [item for item in self._read() if (item.get("collection_id") or item.get("id")) != collection_id]
        self._write(items)

    def clear(self) -> None:
        self._write([])
