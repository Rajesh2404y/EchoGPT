from pydantic import BaseModel, Field, HttpUrl


class YouTubeProcessRequest(BaseModel):
    url: HttpUrl
    title: str | None = None
    language: str | None = Field(default="auto", examples=["auto", "en", "ta", "hi"])


class ChatRequest(BaseModel):
    collection_id: str | None = None
    question: str = Field(min_length=2)
    stream: bool = False


class CollectionRequest(BaseModel):
    collection_id: str


class GenerationRequest(CollectionRequest):
    style: str | None = "concise"
