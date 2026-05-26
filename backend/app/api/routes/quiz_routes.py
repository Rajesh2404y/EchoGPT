from fastapi import APIRouter

from app.models.request_models import GenerationRequest
from app.models.response_models import GeneratedContentResponse
from app.services.quiz_service import QuizService

router = APIRouter(tags=["quiz"])


@router.post("/quiz", response_model=GeneratedContentResponse)
async def quiz(payload: GenerationRequest):
    content = await QuizService().generate(payload.collection_id, payload.style)
    return GeneratedContentResponse(collection_id=payload.collection_id, content=content)
