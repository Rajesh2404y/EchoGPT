from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.security import validate_audio_file
from app.models.response_models import ProcessResponse
from app.services.audio_service import AudioService
from app.services.media_pipeline import MediaPipeline

router = APIRouter(tags=["audio"])


@router.post("/upload-audio", response_model=ProcessResponse)
async def upload_audio(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    language: str | None = Form(default=None),
) -> ProcessResponse:
    settings = get_settings()
    try:
        await validate_audio_file(file, settings.max_upload_mb)
        path = await AudioService().save_upload(file)
        result = await MediaPipeline().process_audio(
            path,
            title or file.filename or "Uploaded audio",
            language,
            prefix="audio",
        )
        return ProcessResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/transcribe", response_model=ProcessResponse)
async def transcribe_audio(
    file: UploadFile = File(...), language: str | None = Form(default=None)
) -> ProcessResponse:
    return await upload_audio(file=file, title=file.filename, language=language)
