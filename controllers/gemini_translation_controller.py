import os
import asyncio
from fastapi import APIRouter, Body, Query, Header, HTTPException
from typing import Optional

from models.Translation import Translation
from services.pdf_service import PdfService
from services.gemini_translation_service_impl import GeminiTranslationService

router = APIRouter(
    prefix="/gemini",
    tags=["gemini"]
)

pdf_service = PdfService()

# ✅ Initialize service with model name (api_key will be read inside service.translate)
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")


@router.post("/translate", response_model=Translation)
async def translate(
    file_id: str = Query(...),
    page: int = Query(...),
    columns: int = Query(1, description="Number of text columns"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Accepts either:
      - { "original_text": "..." }
    or
      - { "file_id": "...", "page": 1, "columns": 1 }

    If original_text is not provided, re-uses extraction via pdf_service.
    GEMINI_API_KEY env or X-API-Key header will be used for API calls.
    """
    try:
        extraction = pdf_service.extract_pdf_by_page(file_id=file_id, page=page, columns=columns)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PDF not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")

    original_text = extraction.get("joined_text")
    if not original_text:
        raise HTTPException(status_code=500, detail="No text extracted for given file/page")

    api_key = x_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=401, detail="No Gemini API key configured. Set GEMINI_API_KEY or provide X-API-Key header.")

    #testing gemini translation service

    gemini_service = GeminiTranslationService(
        model_name=MODEL_NAME,
        api_key=api_key
    )

    translated_text = gemini_service.translate(original_text=original_text)
    return Translation(original_text=original_text, translated_text=translated_text)

