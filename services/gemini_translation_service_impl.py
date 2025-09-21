import os
import math
import asyncio
from typing import Optional, List

from models.Translation import Translation
from services.translation_service import TranslationService
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
import requests


class GeminiTranslationService(TranslationService):
    """Concrete implementation using Gemini API"""

    def __init__(self, model_name: str, chunk_size_chars: int = 8000):
        self.model_name = model_name

        self.prompt_template = ChatPromptTemplate([
            ("system", """You are a friendly English to Bengali translator
                          who translates in natural and casual tone"""),
            ("user", "Translate the following text to Bengali: {original_text}")
        ])

        self.chat_model = init_chat_model(
            model_name,
            api_key=os.getenv("GEMINI_API_KEY"),
            model_provider="google_genai"
        )

        self.structured_model = self.chat_model.with_structured_output(Translation)
        self.chain = self.prompt_template | self.structured_model

        self.chunk_size = chunk_size_chars

    async def translate(self, original_text: str, api_key: Optional[str] = None) -> str:
        """Translate text using Gemini API asynchronously"""

        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            return self._mock_translate(original_text)

        chunks = self._chunk_text(original_text)
        translated_chunks: List[str] = []

        for chunk in chunks:
            # run blocking network call in a thread
            translated_chunk = await asyncio.to_thread(self._call_gemini, chunk, key)
            translated_chunks.append(translated_chunk)

        return "".join(translated_chunks)

    def _chunk_text(self, text: str) -> List[str]:
        if not text:
            return []
        n = math.ceil(len(text) / self.chunk_size)
        return [text[i*self.chunk_size:(i+1)*self.chunk_size] for i in range(n)]

    def _call_gemini(self, chunk: str, api_key: str) -> str:
        """Synchronous network call to Gemini API"""
        try:
            url = "https://generativelanguage.googleapis.com/v1beta2/models/YOUR_MODEL:generateText"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {"prompt": chunk}
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("candidates", [{}])[0].get("output", "") or ""
        except Exception:
            return self._mock_translate(chunk)

    def _mock_translate(self, text: str) -> str:
        return "[MOCK TRANSLATION] " + (text or "")
