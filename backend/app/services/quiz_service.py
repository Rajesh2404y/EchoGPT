from app.services.llm_service import LLMService
from app.services.transcript_service import TranscriptService


class QuizService:
    def __init__(self) -> None:
        self.llm = LLMService()
        self.transcripts = TranscriptService()
        self.system = "You are EchoGPT. Build quizzes only from the provided transcript."

    async def generate(self, collection_id: str, style: str | None = None) -> str:
        transcript = self.transcripts.load(collection_id)["text"]
        prompt = (
            "Generate 8 MCQs with answers and 6 flashcards from this transcript.\n"
            f"Difficulty: {style or 'mixed'}\n\nTranscript:\n{transcript[:12000]}"
        )
        return await self.llm.generate(prompt, self.system)
