from fastapi import APIRouter

from app.models.request_models import GenerationRequest
from app.models.response_models import GeneratedContentResponse
from app.services.notes_service import NotesService

router = APIRouter(tags=["notes"])


@router.post("/notes", response_model=GeneratedContentResponse)
async def notes(payload: GenerationRequest):
    content = await NotesService().generate(payload.collection_id, payload.style)
    return GeneratedContentResponse(collection_id=payload.collection_id, content=content)
