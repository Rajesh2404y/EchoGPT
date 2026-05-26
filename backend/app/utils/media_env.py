import os
from pathlib import Path
from shutil import which

from app.core.config import get_settings


def get_ffmpeg_location() -> str | None:
    settings = get_settings()
    if settings.ffmpeg_location:
        return settings.ffmpeg_location

    ffmpeg_path = which("ffmpeg")
    ffprobe_path = which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return str(Path(ffmpeg_path).parent)
    return None


def ensure_ffmpeg_on_path() -> str:
    location = get_ffmpeg_location()
    if not location:
        raise RuntimeError(
            "ffmpeg and ffprobe are required for transcription and YouTube audio extraction. "
            "Install ffmpeg and add it to PATH, or set FFMPEG_LOCATION in backend/.env "
            "to the folder containing ffmpeg.exe and ffprobe.exe."
        )

    ffmpeg = Path(location) / "ffmpeg.exe"
    ffprobe = Path(location) / "ffprobe.exe"
    if not ffmpeg.exists() or not ffprobe.exists():
        raise RuntimeError(
            f"FFMPEG_LOCATION is set to '{location}', but ffmpeg.exe or ffprobe.exe was not found there."
        )

    current_path = os.environ.get("PATH", "")
    path_parts = current_path.split(os.pathsep) if current_path else []
    if location not in path_parts:
        os.environ["PATH"] = location + os.pathsep + current_path
    return location
