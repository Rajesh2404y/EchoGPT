from app.core.config import get_settings
from app.core.logger import get_logger
from app.services.rerank_service import RerankService
from app.services.vector_service import VectorService

logger = get_logger(__name__)


class RetrievalService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.vector_service = VectorService()
        self.reranker = RerankService()

    def expand_query(self, question: str) -> str:
        normalized = " ".join(question.strip().split())
        lower = normalized.lower()
        expansions = [
            normalized,
            "transcript chapter title timestamp lesson section",
            "definition explanation examples key concepts",
        ]
        if "data model" in lower or "data modeling" in lower or "data modelling" in lower:
            expansions.extend(
                [
                    "building a data model introduction to data modeling",
                    "e-commerce data model ecommerce database schema",
                    "entities attributes relationships tables models",
                    "Django models product customer order cart collection",
                ]
            )
        elif len(normalized.split()) <= 7:
            expansions.append(
                f"Find the transcript section and timestamp related to {normalized}"
            )
        return (
            ". ".join(expansions)
        )

    def retrieve(self, collection_id: str, question: str) -> list[dict]:
        query = self.expand_query(question)
        limit = max(15, self.settings.retrieval_k)
        logger.info("Expanded retrieval query: %s", query)
        candidates = self.vector_service.search(collection_id, query, limit)
        self._log_chunks("Retrieved candidate", candidates)
        ranked = self.reranker.rerank(question, candidates)
        self._log_chunks("Top reranked", ranked)
        selected = ranked[: min(3, self.settings.rerank_top_k)]
        self._log_chunks("Selected for Ollama", selected)
        return selected

    def _log_chunks(self, label: str, chunks: list[dict]) -> None:
        for index, chunk in enumerate(chunks, start=1):
            text = " ".join((chunk.get("text") or "").split())[:300]
            message = (
                f"{label} chunk {index} "
                f"score={chunk.get('score')} "
                f"vector_score={chunk.get('vector_score')} "
                f"rerank_score={chunk.get('rerank_score')} "
                f"lexical_boost={chunk.get('lexical_boost')} "
                f"timestamp={chunk.get('timestamp_label') or chunk.get('timestamp')} "
                f"source={chunk.get('source_url')} "
                f"text={text}"
            )
            logger.info(
                message,
            )
            if self.settings.environment == "development":
                print(message)
