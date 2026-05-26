import os

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService


class VectorService:
    def __init__(self) -> None:
        os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
        import chromadb

        self.settings = get_settings()
        self.client = chromadb.PersistentClient(path=str(self.settings.path(self.settings.chroma_dir)))
        self.embeddings = EmbeddingService()

    def upsert_chunks(self, collection_id: str, chunks: list[dict]) -> None:
        collection = self.client.get_or_create_collection(name=collection_id)
        texts = [chunk["text"] for chunk in chunks]
        vectors = self.embeddings.embed_documents(texts)
        ids = [f"{collection_id}_{index}" for index in range(len(chunks))]
        metadatas = [
            {"start": chunk.get("start") or 0, "end": chunk.get("end") or 0}
            for chunk in chunks
        ]
        collection.upsert(ids=ids, documents=texts, embeddings=vectors, metadatas=metadatas)

    def search(self, collection_id: str, query: str, limit: int) -> list[dict]:
        collection = self.client.get_or_create_collection(name=collection_id)
        vector = self.embeddings.embed_query(query)
        result = collection.query(query_embeddings=[vector], n_results=limit)
        documents = result.get("documents", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        matches = []
        for text, distance, metadata in zip(documents, distances, metadatas, strict=False):
            matches.append(
                {
                    "text": text,
                    "score": 1 - float(distance),
                    "start": metadata.get("start"),
                    "end": metadata.get("end"),
                }
            )
        return matches

    def delete_collection(self, collection_id: str) -> None:
        self.client.delete_collection(name=collection_id)
