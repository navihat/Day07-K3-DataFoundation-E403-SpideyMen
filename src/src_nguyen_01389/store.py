from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata)
        metadata.setdefault("doc_id", doc.id)
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_vec = self._embedding_fn(query)
        scored = [(_dot(query_vec, rec["embedding"]), rec) for rec in records]
        scored.sort(key=lambda item: item[0], reverse=True)
        results = []
        for score, rec in scored[:top_k]:
            results.append(
                {
                    "id": rec["id"],
                    "content": rec["content"],
                    "metadata": rec["metadata"],
                    "score": score,
                }
            )
        return results

    def add_documents(self, docs: list[Document]) -> None:
        records = [self._make_record(doc) for doc in docs]
        if self._use_chroma and self._collection is not None:
            self._collection.add(
                ids=[f"{r['id']}#{index}" for index, r in enumerate(records, start=self._next_index)],
                documents=[r["content"] for r in records],
                embeddings=[r["embedding"] for r in records],
                metadatas=[r["metadata"] for r in records],
            )
            self._next_index += len(records)
        else:
            self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self._use_chroma and self._collection is not None:
            response = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=top_k,
            )
            results = []
            ids = (response.get("ids") or [[]])[0]
            documents = (response.get("documents") or [[]])[0]
            metadatas = (response.get("metadatas") or [[]])[0]
            distances = (response.get("distances") or [[]])[0]
            for index, doc_id in enumerate(ids):
                results.append(
                    {
                        "id": doc_id,
                        "content": documents[index],
                        "metadata": metadatas[index],
                        "score": distances[index],
                    }
                )
            return results
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        if not metadata_filter:
            return self.search(query, top_k=top_k)
        if self._use_chroma and self._collection is not None:
            response = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=top_k,
                where=metadata_filter,
            )
            results = []
            ids = (response.get("ids") or [[]])[0]
            documents = (response.get("documents") or [[]])[0]
            metadatas = (response.get("metadatas") or [[]])[0]
            distances = (response.get("distances") or [[]])[0]
            for index, doc_id in enumerate(ids):
                results.append(
                    {
                        "id": doc_id,
                        "content": documents[index],
                        "metadata": metadatas[index],
                        "score": distances[index],
                    }
                )
            return results
        filtered = [
            rec
            for rec in self._store
            if all(rec["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        if self._use_chroma and self._collection is not None:
            self._collection.delete(where={"doc_id": doc_id})
            return True
        before = len(self._store)
        self._store = [
            rec
            for rec in self._store
            if rec["id"] != doc_id and rec["metadata"].get("doc_id") != doc_id
        ]
        return len(self._store) < before