# EchoGPT

EchoGPT is an AI-powered Universal Media Knowledge Assistant: ChatGPT for YouTube videos and audio files.

Users can paste a YouTube URL or upload audio, then EchoGPT transcribes the content, chunks the transcript, stores embeddings in ChromaDB, and answers questions with a RAG pipeline powered by Ollama and Qwen3:8b.

## Features

- YouTube audio extraction with `yt-dlp`
- Audio upload for mp3, wav, and m4a
- Whisper transcription with timestamp segments
- Transcript cleanup and 500/100 chunking
- `BAAI/bge-small-en` embeddings
- ChromaDB persistent vector storage
- Semantic retrieval and cross-encoder reranking
- Qwen3:8b responses through Ollama
- Summary, notes, quiz, timestamps, history, and transcript search
- React, Vite, Tailwind, Framer Motion frontend
- FastAPI backend with Docker support

## Quick Start

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

LLM:

```bash
ollama pull qwen3:8b
ollama serve
```

Open `http://localhost:5173`.

## Project Structure

- `frontend/`: React application
- `backend/`: FastAPI application and AI services
- `docker/`: Docker Compose deployment
- `docs/`: architecture, API, and setup documentation

## API

Main endpoints:

- `POST /process-youtube`
- `POST /upload-audio`
- `POST /transcribe`
- `POST /ask`
- `POST /summary`
- `POST /notes`
- `POST /quiz`
- `GET /history`
- `DELETE /history/{id}`

## License

MIT
