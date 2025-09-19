from pydantic import BaseModel
from typing import Optional


class TranslationModel(BaseModel):
    model_name: str
    api_key: Optional[str]
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
