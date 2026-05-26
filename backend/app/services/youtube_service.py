from pathlib import Path

from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.media_env import ensure_ffmpeg_on_path

logger = get_logger(__name__)


class YouTubeService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def download_audio(self, url: str) -> tuple[Path, str]:
        import yt_dlp

        ffmpeg_location = ensure_ffmpeg_on_path()
        output_template = str(self.settings.path(self.settings.temp_dir) / "%(id)s.%(ext)s")
        options = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "ffmpeg_location": ffmpeg_location,
            "quiet": True,
            "noplaylist": True,
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
            info = ydl.extract_info(url, download=True)
            video_id = info["id"]
            title = info.get("title") or "YouTube media"
        return self.settings.path(self.settings.temp_dir) / f"{video_id}.mp3", title
