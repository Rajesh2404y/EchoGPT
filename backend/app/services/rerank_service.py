from functools import lru_cache
import os

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_reranker(model_name: str):
    from sentence_transformers import CrossEncoder

    settings = get_settings()
    cache_dir = str(settings.path(settings.hf_cache_dir))
    os.environ.setdefault("HF_HOME", cache_dir)
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache_dir)
    logger.info("Loading reranker model: %s", model_name)
    return CrossEncoder(
        model_name,
        automodel_args={"cache_dir": cache_dir, "local_files_only": True},
        tokenizer_args={"local_files_only": True},
        config_args={"local_files_only": True},
    )


class RerankService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def rerank(self, question: str, chunks: list[dict]) -> list[dict]:
        if not chunks:
            return []
        try:
            model = _load_reranker(self.settings.reranker_model)
            pairs = [(question, chunk["text"]) for chunk in chunks]
            scores = model.predict(pairs)
            ranked = []
            for chunk, score in zip(chunks, scores, strict=False):
                ranked.append({**chunk, "score": float(score)})
            return sorted(ranked, key=lambda item: item["score"], reverse=True)[
                : self.settings.rerank_top_k
            ]
        except Exception as exc:
            logger.warning("Reranker unavailable, using vector scores only: %s", exc)
            return chunks[: self.settings.rerank_top_k]
