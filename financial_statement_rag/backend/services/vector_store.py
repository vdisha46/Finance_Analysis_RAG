from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import faiss
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.config import VECTORSTORE_DIR
from backend.services.gemini_service import get_embedding_model


class VectorStoreManager:
    """Build and query a local FAISS vector store for uploaded documents."""

    def __init__(self, index_name: str = "financial_docs"):
        self.index_name = index_name
        self.vectorstore_dir = VECTORSTORE_DIR
        self.index_path = self.vectorstore_dir / f"{index_name}.faiss"
        self.metadata_path = self.vectorstore_dir / f"{index_name}.pkl"

    def create_vector_store(self, documents: list[Document]) -> FAISS:
        embedding_model = get_embedding_model()
        if embedding_model is None:
            raise ValueError("Gemini embedding model is unavailable. Missing GEMINI_API_KEY.")
        vector_store = FAISS.from_documents(documents, embedding_model)
        self.save_vector_store(vector_store)
        return vector_store

    def save_vector_store(self, vector_store: FAISS) -> None:
        vector_store.save_local(folder_path=str(self.vectorstore_dir), index_name=self.index_name)

    def load_vector_store(self) -> FAISS | None:
        embedding_model = get_embedding_model()
        if embedding_model is None:
            return None
        if not self.index_path.exists() or not self.metadata_path.exists():
            return None
        return FAISS.load_local(folder_path=str(self.vectorstore_dir), index_name=self.index_name, embeddings=embedding_model, allow_dangerous_deserialization=True)

    def add_documents(self, documents: list[Document]) -> FAISS:
        vector_store = self.load_vector_store()
        embedding_model = get_embedding_model()
        if embedding_model is None:
            raise ValueError("Gemini embedding model is unavailable. Missing GEMINI_API_KEY.")
        if vector_store is None:
            return self.create_vector_store(documents)
        vector_store.add_documents(documents)
        self.save_vector_store(vector_store)
        return vector_store

    def search_documents(self, query: str, k: int = 5) -> list[Document]:
        vector_store = self.load_vector_store()
        if vector_store is None:
            return []
        return vector_store.similarity_search(query, k=k)
