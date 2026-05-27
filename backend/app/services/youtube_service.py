from pathlib import Path

from app.core.config import get_settings
from app.core.logger import get_logger
from app.services.ffmpeg_service import FFmpegService
from app.utils.media_env import ensure_ffmpeg_on_path

logger = get_logger(__name__)


class YouTubeService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _progress_hook(self, status: dict) -> None:
        if status.get("status") == "downloading":
            downloaded = status.get("downloaded_bytes") or 0
            total = status.get("total_bytes") or status.get("total_bytes_estimate") or 0
            if total:
                logger.info(
                    "YouTube download progress: %.1f%%",
                    downloaded / total * 100,
                )
            return
        if status.get("status") == "finished":
            logger.info("YouTube download finished, extracting audio")

    def _best_audio_format(self, info: dict) -> dict | None:
        formats = info.get("formats") or []
        audio_formats = [
            item
            for item in formats
            if item.get("url") and item.get("acodec") != "none" and item.get("vcodec") == "none"
        ]
        if not audio_formats:
            audio_formats = [item for item in formats if item.get("url") and item.get("acodec") != "none"]
        if not audio_formats:
            return info if info.get("url") else None
        audio_formats.sort(
            key=lambda item: (
                item.get("abr") or 0,
                item.get("filesize") or item.get("filesize_approx") or 0,
            ),
            reverse=True,
        )
        return audio_formats[0]

    async def download_audio(
        self, url: str, max_seconds: int | None = None
    ) -> tuple[Path, str, str, str, int | None]:
        import yt_dlp

        ffmpeg_location = ensure_ffmpeg_on_path()
        output_template = str(self.settings.path(self.settings.temp_dir) / "%(id)s.%(ext)s")
        options = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "ffmpeg_location": ffmpeg_location,
            "quiet": True,
            "noplaylist": True,
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "socket_timeout": 60,
            "progress_hooks": [self._progress_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
        logger.info("Downloading YouTube audio: %s", url)
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=max_seconds is None)
            video_id = info["id"]
            title = info.get("title") or "YouTube media"
            source_url = info.get("webpage_url") or url
            duration = info.get("duration")
            if max_seconds is not None:
                audio_format = self._best_audio_format(info)
                if not audio_format:
                    raise RuntimeError("Could not resolve a YouTube audio stream.")
                audio_path = self.settings.path(self.settings.temp_dir) / f"{video_id}_first_{max_seconds}s.mp3"
                if not audio_path.exists():
                    FFmpegService().extract_audio_clip(
                        audio_format["url"],
                        audio_path,
                        max_seconds,
                        headers=audio_format.get("http_headers") or info.get("http_headers"),
                    )
            else:
                audio_path = self.settings.path(self.settings.temp_dir) / f"{video_id}.mp3"
        logger.info(
            "YouTube audio ready: video_id=%s duration=%s processed_limit=%s title=%s",
            video_id,
            duration,
            "full" if max_seconds is None else max_seconds,
            title,
        )
        return audio_path, title, video_id, source_url, max_seconds
