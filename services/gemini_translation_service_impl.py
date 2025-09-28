from models.Translation import Translation
from services.translation_service import TranslationService

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


class GeminiTranslationService(TranslationService):
    """Concrete implementation of TranslationService using Gemini API"""

    def __init__(self, model_name: str, api_key: str):

        self.prompt_template = ChatPromptTemplate([
            ("system", """You are a friendly English to Bengali translator
             who translates in natural and casual tone"""),
            ("user",
             "Translate the following text to Bengali: {original_text}")
        ])

        self.chat_model = init_chat_model(
            model_name,
            api_key=api_key,
            model_provider="google_genai"
        )

        self.structured_model = self.chat_model.with_structured_output(
            Translation
        )

        self.chain = self.prompt_template | self.structured_model

    def translate(self, original_text: str) -> Translation:
        """Translate text using Gemini API"""

        translation = self.chain.invoke(
            original_text
        )

        return translation