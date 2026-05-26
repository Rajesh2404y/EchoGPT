# EchoGPT Architecture

EchoGPT is a media-to-knowledge RAG system. Users provide a YouTube URL or upload audio. The backend extracts audio, transcribes with Whisper, cleans the transcript, chunks it, creates BGE embeddings, persists vectors in ChromaDB, retrieves/reranks relevant chunks, and asks Qwen3:8b through Ollama for grounded answers.

## Flow

1. React frontend sends media to FastAPI.
2. `YouTubeService` downloads audio with `yt-dlp`, or `AudioService` stores uploaded files.
3. `WhisperService` transcribes audio with segment timestamps.
4. `TranscriptService` normalizes and saves transcript JSON.
5. `ChunkService` creates 500-word chunks with 100-word overlap.
6. `VectorService` embeds chunks with `BAAI/bge-small-en` and stores them in ChromaDB.
7. `RetrievalService` performs semantic search and reranks with `cross-encoder/ms-marco-MiniLM-L-6-v2`.
8. `RAGService` injects context into the EchoGPT system prompt and calls Ollama.

## Production Notes

- Run Whisper and embeddings on GPU where possible.
- Keep Ollama near the API server to reduce generation latency.
- Move history metadata to PostgreSQL for multi-user deployments.
- Add Redis for job status, cache, and streaming session state.
- Put media processing behind background workers for large uploads.
