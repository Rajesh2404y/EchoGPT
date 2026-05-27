import os

from app.core.config import get_settings
from app.core.logger import get_logger
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)


class VectorService:
    def __init__(self) -> None:
        os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
        os.environ.setdefault("CHROMA_TELEMETRY", "False")
        import chromadb
        from chromadb.config import Settings

        self.settings = get_settings()
        self.client = chromadb.PersistentClient(
            path=str(self.settings.path(self.settings.chroma_dir)),
            settings=Settings(anonymized_telemetry=False),
        )
        self.embeddings = EmbeddingService()

    def upsert_chunks(self, collection_id: str, chunks: list[dict]) -> None:
        collection = self.client.get_or_create_collection(name=collection_id)
        total = len(chunks)
        batch_size = 16
        logger.info("Vector indexing started: collection=%s chunks=%s", collection_id, total)
        for start in range(0, total, batch_size):
            batch = chunks[start : start + batch_size]
            texts = [chunk["text"] for chunk in batch]
            vectors = self.embeddings.embed_documents(texts, batch_size=batch_size)
            ids = [f"{collection_id}_{index}" for index in range(start, start + len(batch))]
            metadatas = [
                {
                    "timestamp": float(chunk.get("timestamp") or chunk.get("start") or 0),
                    "timestamp_label": str(chunk.get("timestamp_label") or ""),
                    "start": float(chunk.get("start") or 0),
                    "end": float(chunk.get("end") or 0),
                    "video_id": str(chunk.get("video_id") or ""),
                    "source_url": str(chunk.get("source_url") or ""),
                    "collection_id": str(chunk.get("collection_id") or collection_id),
                }
                for chunk in batch
            ]
            collection.upsert(ids=ids, documents=texts, embeddings=vectors, metadatas=metadatas)
            logger.info(
                "Vector indexing progress: collection=%s chunks=%s/%s",
                collection_id,
                min(start + len(batch), total),
                total,
            )
        logger.info("Vector indexing finished: collection=%s chunks=%s", collection_id, total)

    def search(self, collection_id: str, query: str, limit: int) -> list[dict]:
        collection = self.client.get_or_create_collection(name=collection_id)
        vector = self.embeddings.embed_query(query)
        result = collection.query(query_embeddings=[vector], n_results=limit)
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        matches = []
        for chunk_id, text, distance, metadata in zip(
            ids, documents, distances, metadatas, strict=False
        ):
            vector_score = 1 - float(distance)
            matches.append(
                {
                    "id": chunk_id,
                    "text": text,
                    "score": vector_score,
                    "vector_score": vector_score,
                    "timestamp": metadata.get("timestamp"),
                    "timestamp_label": metadata.get("timestamp_label"),
                    "start": metadata.get("start"),
                    "end": metadata.get("end"),
                    "video_id": metadata.get("video_id"),
                    "source_url": metadata.get("source_url"),
                }
            )
        logger.info("Vector search returned %s chunks for query=%r", len(matches), query)
        return matches

    def delete_collection(self, collection_id: str) -> None:
        self.client.delete_collection(name=collection_id)
