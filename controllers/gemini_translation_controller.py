from models.Translation import Translation
from services.gemini_translation_service_impl import GeminiTranslationService

from fastapi import APIRouter, Header

router = APIRouter(
    prefix="/gemini",
    tags=["gemini"]
)


@router.post("/translate")
def translate(
    original_text: str,
    x_api_key: str = Header(..., alias="X-API-Key")
) -> Translation:
    """Translate text using Gemini API"""

    gemini_service = GeminiTranslationService(
        model_name="gemini-2.0-flash-lite",
        api_key=x_api_key
    )

    translation = gemini_service.translate(original_text)
    return translation
