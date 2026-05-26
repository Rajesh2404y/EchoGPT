from fastapi import APIRouter

from app.models.request_models import GenerationRequest
from app.models.response_models import GeneratedContentResponse
from app.services.history_service import HistoryService
from app.services.summary_service import SummaryService

router = APIRouter(tags=["summary"])


@router.post("/summary", response_model=GeneratedContentResponse)
async def summary(payload: GenerationRequest):
    content = await SummaryService().generate(payload.collection_id, payload.style)
    HistoryService().append_generated_content(payload.collection_id, "summary", content)
    return GeneratedContentResponse(collection_id=payload.collection_id, content=content)
