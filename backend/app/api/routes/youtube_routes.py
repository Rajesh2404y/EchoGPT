from fastapi import APIRouter, HTTPException

from app.models.request_models import YouTubeProcessRequest
from app.models.response_models import ProcessResponse
from app.services.media_pipeline import MediaPipeline
from app.services.youtube_service import YouTubeService

router = APIRouter(tags=["youtube"])


@router.post("/process-youtube", response_model=ProcessResponse)
async def process_youtube(payload: YouTubeProcessRequest) -> ProcessResponse:
    try:
        audio_path, detected_title, video_id, source_url, processed_seconds = await YouTubeService().download_audio(
            str(payload.url),
            max_seconds=None,
        )
        result = await MediaPipeline().process_audio(
            audio_path,
            payload.title or detected_title,
            payload.language,
            prefix="yt",
            video_id=video_id,
            source_url=source_url,
            max_seconds=-1,
        )
        return ProcessResponse(**result)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
