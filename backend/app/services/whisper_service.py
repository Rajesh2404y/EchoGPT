from functools import lru_cache
from pathlib import Path
import subprocess

from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.media_env import ensure_ffmpeg_on_path

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    import whisper

    settings = get_settings()
    logger.info("Loading Whisper model: %s", model_name)
    return whisper.load_model(
        model_name,
        download_root=str(settings.path(settings.whisper_cache_dir)),
    )


class WhisperService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _prepare_audio(self, audio_path: Path) -> Path:
        max_seconds = self.settings.max_transcription_seconds
        ffmpeg_dir = Path(ensure_ffmpeg_on_path())
        suffix = f"_first_{max_seconds}s" if max_seconds > 0 else ""
        prepared_path = self.settings.path(self.settings.temp_dir) / (
            f"{audio_path.stem}{suffix}_prepared.wav"
        )
        if prepared_path.exists():
            logger.info("Using prepared audio for transcription: %s", prepared_path)
            return prepared_path

        logger.info("Preparing audio for Whisper: %s", audio_path)
        command = [
            str(ffmpeg_dir / "ffmpeg.exe"),
            "-y",
        ]
        if max_seconds > 0:
            command.extend(["-t", str(max_seconds)])
        command.extend(
            [
            "-i",
            str(audio_path),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-af",
            "loudnorm,afftdn",
            ]
        )
        command.append(str(prepared_path))
        subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info("Prepared audio created: %s", prepared_path)
        return prepared_path

    def _transcription_options(self, language: str | None) -> dict:
        normalized_language = (language or "auto").strip().lower()
        options = {
            "fp16": False,
            "beam_size": 5,
            "best_of": 5,
            "temperature": 0,
            "condition_on_previous_text": False,
        }
        if normalized_language and normalized_language != "auto":
            options["language"] = normalized_language
        return options

    async def transcribe(self, audio_path: Path, language: str | None = None) -> dict:
        ensure_ffmpeg_on_path()
        prepared_audio = self._prepare_audio(audio_path)
        model = _load_model(self.settings.whisper_model)
        options = self._transcription_options(language)
        logger.info("Whisper transcription options: %s", options)
        result = model.transcribe(str(prepared_audio), **options)
        return {
            "text": result.get("text", ""),
            "language": result.get("language", language or "auto"),
            "segments": result.get("segments", []),
        }
