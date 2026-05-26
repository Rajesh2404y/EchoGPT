from fastapi import HTTPException, UploadFile, status

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
}


async def validate_audio_file(file: UploadFile, max_upload_mb: int) -> None:
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload an mp3, wav, or m4a audio file.",
        )

    size = 0
    while chunk := await file.read(1024 * 1024):
        size += len(chunk)
        if size > max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Audio file is too large.")
    await file.seek(0)
