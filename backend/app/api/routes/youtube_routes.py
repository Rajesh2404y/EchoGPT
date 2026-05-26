from fastapi import APIRouter, HTTPException

from app.models.request_models import YouTubeProcessRequest
from app.models.response_models import ProcessResponse
from app.services.media_pipeline import MediaPipeline
from app.services.youtube_service import YouTubeService

router = APIRouter(tags=["youtube"])


@router.post("/process-youtube", response_model=ProcessResponse)
async def process_youtube(payload: YouTubeProcessRequest) -> ProcessResponse:
    try:
        audio_path, detected_title = await YouTubeService().download_audio(str(payload.url))
        result = await MediaPipeline().process_audio(
            audio_path,
            payload.title or detected_title,
            payload.language,
            prefix="yt",
        )
        return ProcessResponse(**result)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
