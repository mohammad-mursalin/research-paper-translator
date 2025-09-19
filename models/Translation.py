from pydantic import BaseModel


class Translation(BaseModel):
    original_text: str
    translated_text: str
