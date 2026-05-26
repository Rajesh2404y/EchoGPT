from app.services.llm_service import LLMService
from app.services.transcript_service import TranscriptService


class NotesService:
    def __init__(self) -> None:
        self.llm = LLMService()
        self.transcripts = TranscriptService()
        self.system = "You are EchoGPT. Create study notes only from the provided transcript."

    async def generate(self, collection_id: str, style: str | None = None) -> str:
        transcript = self.transcripts.load(collection_id)["text"]
        prompt = (
            "Create structured notes with headings, bullet points, key ideas, and action items.\n"
            f"Style: {style or 'study'}\n\nTranscript:\n{transcript[:12000]}"
        )
        return await self.llm.generate(prompt, self.system)
