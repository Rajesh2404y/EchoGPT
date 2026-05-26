from functools import lru_cache
import os

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_embedding_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    cache_dir = str(settings.path(settings.hf_cache_dir))
    os.environ.setdefault("HF_HOME", cache_dir)
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache_dir)
    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name, cache_folder=cache_dir, local_files_only=True)


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = _load_embedding_model(self.settings.embedding_model)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()
