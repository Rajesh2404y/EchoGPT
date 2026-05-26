from app.core.config import get_settings
from app.services.rerank_service import RerankService
from app.services.vector_service import VectorService


class RetrievalService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.vector_service = VectorService()
        self.reranker = RerankService()

    def retrieve(self, collection_id: str, question: str) -> list[dict]:
        candidates = self.vector_service.search(collection_id, question, self.settings.retrieval_k)
        return self.reranker.rerank(question, candidates)
