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

    def embed_documents(self, texts: list[str], batch_size: int = 16) -> list[list[float]]:
        if not texts:
            return []
        passages = [f"Represent this passage for retrieval: {text}" for text in texts]
        vectors: list[list[float]] = []
        total = len(passages)
        for start in range(0, total, batch_size):
            batch = passages[start : start + batch_size]
            logger.info(
                "Embedding batch %s-%s of %s",
                start + 1,
                min(start + len(batch), total),
                total,
            )
            batch_vectors = self.model.encode(batch, normalize_embeddings=True).tolist()
            vectors.extend(batch_vectors)
        logger.info("Embedding finished: documents=%s", total)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        query = f"Represent this sentence for searching relevant passages: {text}"
        return self.model.encode([query], normalize_embeddings=True)[0].tolist()
