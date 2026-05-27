from pathlib import Path
import subprocess

from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.media_env import ensure_ffmpeg_on_path

logger = get_logger(__name__)


class FFmpegService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.ffmpeg_dir = Path(ensure_ffmpeg_on_path())

    def executable(self, name: str) -> str:
        windows_path = self.ffmpeg_dir / f"{name}.exe"
        if windows_path.exists():
            return str(windows_path)
        unix_path = self.ffmpeg_dir / name
        if unix_path.exists():
            return str(unix_path)
        return str(windows_path)

    def probe_duration(self, media_path: Path) -> float | None:
        command = [
            self.executable("ffprobe"),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        try:
            return float(result.stdout.strip())
        except ValueError:
            return None

    def extract_audio_clip(
        self,
        input_url: str,
        output_path: Path,
        limit_seconds: int | None,
        headers: dict[str, str] | None = None,
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.executable("ffmpeg"),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
        ]
        if headers:
            header_blob = "".join(f"{key}: {value}\r\n" for key, value in headers.items())
            command.extend(["-headers", header_blob])
        if limit_seconds is not None:
            command.extend(["-t", str(limit_seconds)])
        command.extend(
            [
                "-i",
                input_url,
                "-vn",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-b:a",
                "96k",
                str(output_path),
            ]
        )
        logger.info(
            "FFmpeg audio extraction started: output=%s limit=%s",
            output_path,
            "full" if limit_seconds is None else limit_seconds,
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info("FFmpeg audio extraction finished: %s", output_path)
        return output_path

    def prepare_wav(
        self,
        input_path: Path,
        output_path: Path,
        limit_seconds: int | None = None,
        offset_seconds: int | None = None,
        denoise: bool = True,
    ) -> Path:
        command = [
            self.executable("ffmpeg"),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
        ]
        if offset_seconds is not None:
            command.extend(["-ss", str(offset_seconds)])
        if limit_seconds is not None:
            command.extend(["-t", str(limit_seconds)])
        command.extend(["-i", str(input_path), "-ar", "16000", "-ac", "1"])
        if denoise:
            command.extend(["-af", "loudnorm,afftdn"])
        command.append(str(output_path))
        subprocess.run(command, check=True, capture_output=True, text=True)
        return output_path
