class TimestampService:
    def from_segments(self, segments: list[dict]) -> list[dict]:
        return [
            {
                "start": float(segment.get("start", 0)),
                "end": float(segment.get("end", 0)),
                "text": segment.get("text", ""),
            }
            for segment in segments
        ]
