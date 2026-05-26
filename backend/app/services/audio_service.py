from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile

from app.core.config import get_settings


class AudioService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def save_upload(self, file: UploadFile) -> Path:
        suffix = Path(file.filename or "audio.mp3").suffix.lower()
        target = self.settings.path(self.settings.upload_dir) / f"{uuid4().hex}{suffix}"
        with target.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return target
