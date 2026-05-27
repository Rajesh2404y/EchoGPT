import asyncio
from functools import lru_cache
from pathlib import Path
import subprocess

from app.core.config import get_settings
from app.core.logger import get_logger
from app.services.ffmpeg_service import FFmpegService
from app.utils.media_env import ensure_ffmpeg_on_path

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    settings = get_settings()
    try:
        from faster_whisper import WhisperModel

        logger.info(
            "Loading faster-whisper model: %s compute_type=%s",
            model_name,
            settings.whisper_compute_type,
        )
        return (
            "faster-whisper",
            WhisperModel(
                model_name,
                device="cpu",
                compute_type=settings.whisper_compute_type,
                download_root=str(settings.path(settings.whisper_cache_dir)),
            ),
        )
    except ImportError:
        import whisper

        logger.info("Loading OpenAI Whisper model: %s", model_name)
        return (
            "openai-whisper",
            whisper.load_model(
                model_name,
                download_root=str(settings.path(settings.whisper_cache_dir)),
            ),
        )


class WhisperService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _transcription_limit(self, override_seconds: int | None = None) -> int | None:
        limit = self.settings.max_transcription_seconds if override_seconds is None else override_seconds
        if limit == -1:
            return None
        return max(1, limit)

    def _audio_duration(self, audio_path: Path, ffmpeg_dir: Path) -> float | None:
        return FFmpegService().probe_duration(audio_path)

    def _prepared_audio_is_complete(
        self,
        source_path: Path,
        prepared_path: Path,
        ffmpeg_dir: Path,
        limit_seconds: int | None,
    ) -> bool:
        if not prepared_path.exists():
            return False
        source_duration = self._audio_duration(source_path, ffmpeg_dir)
        prepared_duration = self._audio_duration(prepared_path, ffmpeg_dir)
        if source_duration is None or prepared_duration is None:
            return False
        expected_duration = source_duration if limit_seconds is None else min(source_duration, limit_seconds)
        return prepared_duration >= max(0, expected_duration - 1)

    def _prepare_audio(self, audio_path: Path, max_seconds: int | None = None) -> Path:
        ffmpeg = FFmpegService()
        ffmpeg_dir = Path(ensure_ffmpeg_on_path())
        limit_seconds = self._transcription_limit(max_seconds)
        suffix = "full" if limit_seconds is None else f"first_{limit_seconds}s"
        prepared_path = self.settings.path(self.settings.temp_dir) / (
            f"{audio_path.stem}_{suffix}_prepared.wav"
        )
        source_duration = self._audio_duration(audio_path, ffmpeg_dir)
        logger.info(
            "Preparing audio for Whisper: source=%s duration=%s limit=%s",
            audio_path,
            source_duration,
            "unlimited" if limit_seconds is None else limit_seconds,
        )
        if self._prepared_audio_is_complete(
            audio_path, prepared_path, ffmpeg_dir, limit_seconds
        ):
            logger.info("Using prepared audio for transcription: %s", prepared_path)
            return prepared_path

        logger.info("Creating prepared audio for transcription: %s", prepared_path)
        temp_path = prepared_path.with_suffix(".tmp.wav")
        ffmpeg.prepare_wav(audio_path, temp_path, limit_seconds=limit_seconds)
        temp_path.replace(prepared_path)
        prepared_duration = self._audio_duration(prepared_path, ffmpeg_dir)
        logger.info(
            "Prepared audio created: %s duration=%s", prepared_path, prepared_duration
        )
        return prepared_path

    def _transcription_options(self, language: str | None) -> dict:
        normalized_language = (language or "auto").strip().lower()
        options = {
            "fp16": False,
            "beam_size": 1,
            "best_of": 1,
            "temperature": 0,
            "condition_on_previous_text": False,
        }
        if normalized_language and normalized_language != "auto":
            options["language"] = normalized_language
        return options

    def _extract_window(
        self,
        prepared_audio: Path,
        offset_seconds: int,
        duration_seconds: int,
        ffmpeg_dir: Path,
    ) -> Path:
        window_path = self.settings.path(self.settings.temp_dir) / (
            f"{prepared_audio.stem}_window_{offset_seconds}_{duration_seconds}.wav"
        )
        window_duration = (
            self._audio_duration(window_path, ffmpeg_dir) if window_path.exists() else None
        )
        if window_duration is not None and window_duration >= max(0, duration_seconds - 1):
            return window_path
        temp_path = window_path.with_suffix(".tmp.wav")
        command = [
            FFmpegService().executable("ffmpeg"),
            "-y",
            "-ss",
            str(offset_seconds),
            "-t",
            str(duration_seconds),
            "-i",
            str(prepared_audio),
            "-ar",
            "16000",
            "-ac",
            "1",
            str(temp_path),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        temp_path.replace(window_path)
        return window_path

    async def _transcribe_window(
        self,
        model_bundle,
        window_path: Path,
        offset_seconds: int,
        options: dict,
        index: int,
        total: int,
    ) -> dict:
        logger.info(
            "Whisper window %s/%s started: offset=%ss audio=%s",
            index,
            total,
            offset_seconds,
            window_path,
        )
        engine, model = model_bundle
        if engine == "faster-whisper":
            result = await asyncio.to_thread(
                self._transcribe_with_faster_whisper,
                model,
                window_path,
                options,
            )
        else:
            result = await asyncio.to_thread(model.transcribe, str(window_path), **options)
        segments = []
        for segment in result.get("segments", []):
            adjusted = dict(segment)
            adjusted["start"] = float(segment.get("start", 0)) + offset_seconds
            adjusted["end"] = float(segment.get("end", 0)) + offset_seconds
            segments.append(adjusted)
        logger.info(
            "Whisper window %s/%s finished: segments=%s text_chars=%s",
            index,
            total,
            len(segments),
            len(result.get("text", "")),
        )
        return {
            "text": result.get("text", ""),
            "language": result.get("language"),
            "segments": segments,
        }

    def _transcribe_with_faster_whisper(self, model, window_path: Path, options: dict) -> dict:
        kwargs = {
            "beam_size": options["beam_size"],
            "condition_on_previous_text": options["condition_on_previous_text"],
        }
        if options.get("language"):
            kwargs["language"] = options["language"]
        segments_iter, info = model.transcribe(str(window_path), **kwargs)
        segments = [
            {
                "start": float(segment.start),
                "end": float(segment.end),
                "text": segment.text,
            }
            for segment in segments_iter
        ]
        return {
            "text": " ".join(segment["text"].strip() for segment in segments),
            "language": getattr(info, "language", None),
            "segments": segments,
        }

    async def transcribe(
        self, audio_path: Path, language: str | None = None, max_seconds: int | None = None
    ) -> dict:
        ffmpeg_dir = Path(ensure_ffmpeg_on_path())
        prepared_audio = self._prepare_audio(audio_path, max_seconds=max_seconds)
        model = _load_model(self.settings.whisper_model)
        options = self._transcription_options(language)
        prepared_duration = self._audio_duration(prepared_audio, ffmpeg_dir) or 0
        window_seconds = max(60, self.settings.transcription_window_seconds)
        logger.info(
            "Whisper transcription started: audio=%s duration=%s window=%s options=%s",
            prepared_audio,
            prepared_duration,
            window_seconds,
            options,
        )
        windows = [
            (offset, min(window_seconds, int(prepared_duration - offset) or window_seconds))
            for offset in range(0, max(1, int(prepared_duration)), window_seconds)
        ]
        if not windows:
            windows = [(0, window_seconds)]

        parts = []
        for index, (offset, duration) in enumerate(windows, start=1):
            window_path = self._extract_window(prepared_audio, offset, duration, ffmpeg_dir)
            parts.append(
                await self._transcribe_window(
                    model,
                    window_path,
                    offset,
                    options,
                    index,
                    len(windows),
                )
            )

        text = " ".join(part.get("text", "").strip() for part in parts if part.get("text"))
        segments = [
            segment
            for part in parts
            for segment in part.get("segments", [])
        ]
        detected_language = next(
            (part.get("language") for part in parts if part.get("language")),
            language or "auto",
        )
        logger.info(
            "Whisper transcription finished: segments=%s text_chars=%s",
            len(segments),
            len(text),
        )
        return {
            "text": text,
            "language": detected_language,
            "segments": segments,
        }
