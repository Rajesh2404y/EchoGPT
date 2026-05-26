# EchoGPT Setup Guide

## Prerequisites

- Python 3.11 recommended
- Node.js 20+
- ffmpeg installed and available on `PATH`
- Ollama installed locally

On Windows, install ffmpeg with:

```bash
winget install Gyan.FFmpeg
```

If ffmpeg is not on `PATH`, set `FFMPEG_LOCATION` in `backend/.env` to the folder that contains `ffmpeg.exe` and `ffprobe.exe`.

For slower CPU-only laptops, set `MAX_TRANSCRIPTION_SECONDS=180` in `backend/.env` while testing. Set it back to `0` to transcribe the full file.

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Pull the local LLM:

```bash
ollama pull qwen3:8b
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Docker

```bash
cd docker
docker compose up --build
```

After the Ollama container starts, pull `qwen3:8b` inside that environment if it is not already present.
