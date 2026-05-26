# EchoGPT API

Base URL: `http://localhost:8000`

## Media

`POST /process-youtube`

```json
{
  "url": "https://youtube.com/watch?v=...",
  "language": "en"
}
```

`POST /upload-audio`

Multipart form fields:

- `file`: mp3, wav, or m4a
- `title`: optional
- `language`: optional `en`, `ta`, `hi`

Both return:

```json
{
  "collection_id": "yt_abcd1234",
  "title": "Media title",
  "transcript": "...",
  "timestamps": [{ "start": 0, "end": 5.4, "text": "..." }],
  "chunks": 12
}
```

## RAG

`POST /ask`

```json
{
  "collection_id": "yt_abcd1234",
  "question": "What are the main ideas?"
}
```

## Generators

- `POST /summary`
- `POST /notes`
- `POST /quiz`

```json
{
  "collection_id": "yt_abcd1234",
  "style": "concise"
}
```

## History

- `GET /history`
- `DELETE /history/{collection_id}`
