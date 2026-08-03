from __future__ import annotations

import os
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

            persist_dir = os.getenv("CHROMA_PERSIST_DIR")
            client = (
                chromadb.PersistentClient(path=persist_dir)
                if persist_dir
                else chromadb.EphemeralClient()
            )
            self._collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},  # so distance maps back to cosine similarity
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Normalize one document into a stored record (unique id + metadata + embedding)."""
        metadata = dict(doc.metadata or {})
        # Chunks coming from ingest.py already carry doc_id; plain documents do not.
        metadata.setdefault("doc_id", doc.id)

        record = {
            "id": f"{self._collection_name}_{self._next_index}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Rank records by similarity against query, highest score first."""
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)
        results = [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": _dot(query_embedding, record["embedding"]),
            }
            for record in records
        ]
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]

    def _query_chroma(self, query: str, top_k: int, where: dict | None = None) -> list[dict[str, Any]]:
        """Run a ChromaDB similarity query and map it onto the same result shape."""
        if top_k <= 0 or self._collection.count() == 0:
            return []

        response = self._collection.query(
            query_embeddings=[self._embedding_fn(query)],
            n_results=min(top_k, self._collection.count()),
            where=where or None,
        )
        results: list[dict[str, Any]] = []
        for index, doc_id in enumerate(response["ids"][0]):
            distance = response["distances"][0][index]
            results.append(
                {
                    "id": doc_id,
                    "content": response["documents"][0][index],
                    "metadata": response["metadatas"][0][index] or {},
                    "score": 1.0 - distance,  # cosine distance -> cosine similarity
                }
            )
        return results

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        records = [self._make_record(doc) for doc in docs]

        if self._use_chroma:
            self._collection.add(
                ids=[r["id"] for r in records],
                documents=[r["content"] for r in records],
                embeddings=[r["embedding"] for r in records],
                metadatas=[r["metadata"] for r in records],
            )
        else:
            self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma:
            return self._query_chroma(query, top_k)
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k)

        if self._use_chroma:
            if len(metadata_filter) > 1:  # Chroma needs an explicit AND for multi-key filters
                where = {"$and": [{key: value} for key, value in metadata_filter.items()]}
            else:
                where = dict(metadata_filter)
            return self._query_chroma(query, top_k, where=where)

        candidates = [
            record
            for record in self._store
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma:
            matched = self._collection.get(where={"doc_id": doc_id})
            if not matched["ids"]:
                return False
            self._collection.delete(ids=matched["ids"])
            return True

        remaining = [record for record in self._store if record["metadata"].get("doc_id") != doc_id]
        if len(remaining) == len(self._store):
            return False
        self._store = remaining
        return True
