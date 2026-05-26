from collections.abc import Iterable


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
    segments: Iterable[dict], chunk_size: int = 500, overlap: int = 100
) -> list[dict]:
    chunks = []
    current_words: list[str] = []
    current_start: float | None = None
    current_end: float | None = None

    for segment in segments:
        text = segment.get("text", "").strip()
        if not text:
            continue
        words = text.split()
        if current_start is None:
            current_start = float(segment.get("start", 0))
        current_end = float(segment.get("end", current_start or 0))
        current_words.extend(words)

        while len(current_words) >= chunk_size:
            emitted = current_words[:chunk_size]
            chunks.append(
                {"text": " ".join(emitted), "start": current_start, "end": current_end}
            )
            current_words = current_words[chunk_size - overlap :]
            current_start = current_end

    if current_words:
        chunks.append({"text": " ".join(current_words), "start": current_start, "end": current_end})
    return chunks
