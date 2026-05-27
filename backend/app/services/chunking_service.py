from app.core.config import get_settings
from app.services.chunk_service import ChunkService


class ChunkingService(ChunkService):
    """Compatibility wrapper with educational-video chunk defaults."""

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_settings()


__all__ = ["ChunkingService", "ChunkService"]
