from collections.abc import AsyncIterator
from app.core.config import get_settings
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.utils.formatter import format_context


class RAGService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._retrieval: RetrievalService | None = None
        self.llm = LLMService()
        self.system_prompt = (
            self.settings.base_dir / "backend/app/prompts/system_prompt.txt"
        ).read_text(encoding="utf-8")

    @property
    def retrieval(self) -> RetrievalService:
        if self._retrieval is None:
            self._retrieval = RetrievalService()
        return self._retrieval

    def build_prompt(self, question: str, context_chunks: list[dict]) -> str:
        context = format_context(context_chunks)
        return (
            "Use only the top reranked transcript chunks below. "
            "Prefer chunks whose timestamp/topic matches the user question. "
            "If the answer is present, answer directly and cite timestamps.\n\n"
            f"Transcript context:\n{context}\n\nUser question: {question}\n\nAnswer:"
        )

    async def answer(self, collection_id: str, question: str) -> tuple[str, list[dict]]:
        if not collection_id:
            return (
                "Please process a YouTube URL or upload audio first, then ask about that media.",
                [],
            )
        chunks = self.retrieval.retrieve(collection_id, question)
        if not chunks:
            return "I could not find that information in the uploaded media.", []
        prompt = self.build_prompt(question, chunks)
        return await self.llm.generate(prompt, self.system_prompt), chunks

    async def stream_answer(self, collection_id: str, question: str) -> AsyncIterator[str]:
        if not collection_id:
            yield "Please process a YouTube URL or upload audio first, then ask about that media."
            return
        chunks = self.retrieval.retrieve(collection_id, question)
        if not chunks:
            yield "I could not find that information in the uploaded media."
            return
        prompt = self.build_prompt(question, chunks)
        async for token in self.llm.stream(prompt, self.system_prompt):
            yield token
