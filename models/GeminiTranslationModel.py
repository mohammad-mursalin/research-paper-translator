from models.TranslationModel import TranslationModel


class GeminiTranslationModel(TranslationModel):
    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name=model_name, api_key=api_key)
        self.model_name = model_name
        self.api_key = api_key
