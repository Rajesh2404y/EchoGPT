from pydantic import BaseModel


class Timestamp(BaseModel):
    start: float
    end: float
    text: str


class ProcessResponse(BaseModel):
    collection_id: str
    title: str
    transcript: str
    timestamps: list[Timestamp]
    chunks: int


class SourceChunk(BaseModel):
    text: str
    start: float | None = None
    end: float | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str | None = None
    created_at: str | None = None


class HistoryItem(BaseModel):
    id: str | None = None
    chat_id: str | None = None
    collection_id: str
    title: str
    created_at: str
    updated_at: str | None = None
    chunks: int
    summary: str | None = None
    last_message: str | None = None
    type: str | None = None


class HistoryDetail(HistoryItem):
    messages: list[ChatMessage]


class GeneratedContentResponse(BaseModel):
    collection_id: str
    content: str
