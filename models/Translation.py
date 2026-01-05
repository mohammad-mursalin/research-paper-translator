from pydantic import BaseModel


class Translation(BaseModel):
    translated_text: str
