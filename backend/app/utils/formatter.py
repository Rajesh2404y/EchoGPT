def format_context(chunks: list[dict]) -> str:
    lines = []
    for index, chunk in enumerate(chunks, start=1):
        prefix = f"[Source {index}"
        timestamp_label = chunk.get("timestamp_label")
        timestamp = chunk.get("timestamp") or chunk.get("start")
        if timestamp_label:
            prefix += f" @ {timestamp_label}"
        elif timestamp is not None:
            prefix += f" @ {float(timestamp):.1f}s"
        if chunk.get("source_url"):
            prefix += f" | {chunk.get('source_url')}"
        prefix += "]"
        lines.append(f"{prefix} {chunk.get('text', '')}")
    return "\n\n".join(lines)
