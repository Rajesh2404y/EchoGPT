from app.services.llm_service import LLMService
from app.services.transcript_service import TranscriptService


class SummaryService:
    def __init__(self) -> None:
        self.llm = LLMService()
        self.transcripts = TranscriptService()
        self.prompt = "Summarize the transcript clearly with key takeaways and timestamps when useful."
        self.system = "You are EchoGPT. Generate summaries only from the provided transcript."

    async def generate(self, collection_id: str, style: str | None = None) -> str:
        transcript = self.transcripts.load(collection_id)["text"]
        prompt = f"{self.prompt}\nStyle: {style or 'concise'}\n\nTranscript:\n{transcript[:12000]}"
        return await self.llm.generate(prompt, self.system)
