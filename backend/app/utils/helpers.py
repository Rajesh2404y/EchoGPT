from datetime import UTC, datetime
from uuid import uuid4


def new_collection_id(prefix: str = "media") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()
