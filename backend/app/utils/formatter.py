def format_context(chunks: list[dict]) -> str:
    lines = []
    for index, chunk in enumerate(chunks, start=1):
        start = chunk.get("start")
        prefix = f"[Source {index}"
        if start is not None:
            prefix += f" @ {start:.1f}s"
        prefix += "]"
        lines.append(f"{prefix} {chunk.get('text', '')}")
    return "\n\n".join(lines)
