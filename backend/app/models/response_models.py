from pydantic import BaseModel


class Timestamp(BaseModel):
    start: float
    end: float
    text: str


class ProcessResponse(BaseModel):
    success: bool = True
    status: str = "completed"
    collection_id: str
    title: str
    transcript: str
    timestamps: list[Timestamp]
    chunks: int
    is_truncated: bool = False
    processed_seconds: int | None = None


class SourceChunk(BaseModel):
    text: str
    timestamp: float | None = None
    timestamp_label: str | None = None
    start: float | None = None
    end: float | None = None
    score: float | None = None
    rerank_score: float | None = None
    vector_score: float | None = None
    video_id: str | None = None
    source_url: str | None = None


class ChatResponse(BaseModel):
    success: bool = True
    answer: str
    sources: list[SourceChunk]
    status: str = "completed"


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
