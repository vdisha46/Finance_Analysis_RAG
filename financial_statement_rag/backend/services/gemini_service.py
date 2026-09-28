from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from backend.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)
load_dotenv()


def get_chat_model():
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY missing. Returning fallback chat model stub.")
        return None
    try:
        return ChatGoogleGenerativeAI(model="gemini-3.8-flash", api_key=GEMINI_API_KEY)
    except Exception as exc:  # pragma: no cover - fallback for missing key/runtime
        logger.warning("Unable to initialize Gemini chat model: %s", exc)
        return None


def get_embedding_model():
    if not GEMINI_API_KEY:
        return None
    try:
        return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=GEMINI_API_KEY)
    except Exception as exc:  # pragma: no cover
        logger.warning("Unable to initialize Gemini embeddings: %s", exc)
        return None


def generate_response(prompt: str, retriever_docs: list | None = None) -> str:
    if not GEMINI_API_KEY:
        return (
            "Gemini API key is not configured. This application is running in safe fallback mode. "
            "Please provide a valid API key in the .env file to enable real AI responses."
        )
    if not retriever_docs:
        return "No retrieved document context is available."

    context = "\n\n".join(doc.page_content for doc in retriever_docs if hasattr(doc, "page_content"))
    if not context:
        return "No relevant financial content was found in the retrieved documents."

    model = get_chat_model()
    if model is None:
        return "The Gemini model could not be initialized."

    content = model.invoke(prompt + "\n\nContext:\n" + context).content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and isinstance(block.get("text"), str)
        )
    return str(content)
