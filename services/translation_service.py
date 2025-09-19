from abc import ABC, abstractmethod
from models import Translation


class TranslationService(ABC):
    """Absttract base class for translation"""
    @abstractmethod
    def translate(self, original_text: str) -> Translation:
        """Translate text using AI"""
        pass
