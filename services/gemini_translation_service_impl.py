from models.Translation import Translation
from services.translation_service import TranslationService

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


class GeminiTranslationService(TranslationService):
    """Concrete implementation of TranslationService using Gemini API"""

    def __init__(self, model_name: str, api_key: str):

        self.prompt_template = ChatPromptTemplate.from_template(r"""
            You are a highly accurate translator and mathematical equation restorer.

            Your job is to translate the text into clear, modern Bangla **AND** reconstruct any distorted or poorly extracted mathematical equations into proper LaTeX.

            Follow ALL rules below:

            ----------------------------------------------------------
            1. TRANSLATION RULES
            ----------------------------------------------------------
            - Translate ONLY the normal text into simple, modern Bangla.
            - Keep commonly used English technical terms (e.g., algorithm, dataset, model, API, server, database, machine learning).
            - Do NOT add explanations, definitions, or extra information.

            ----------------------------------------------------------
            2. FORMATTING RULES
            ----------------------------------------------------------
            - Preserve the original formatting:
                - line breaks
                - spacing
                - paragraphs
                - bullet points
            - The structure of the output must match the input exactly.

            ----------------------------------------------------------
            3. EQUATION RESTORATION RULES (IMPORTANT)
            ----------------------------------------------------------
            The input text may contain equations extracted from a PDF, often distorted (e.g., missing superscripts, wrong symbols, multiplications instead of powers).

            Your task:

            - Detect any mathematical expression or equation.
            - Understand its intended mathematical meaning.
            - Restore it into a correct mathematical form.
            - Convert it into **LaTeX display mode**:

            \[
            ... restored equation ...
            \]

            Examples of expected fixes (braces escaped for template safety):
            - (a + b){{2}}  →  (a + b)^2
            - x_1 + x_2 / 2 might become → \frac{{x_1 + x_2}}{{2}}
            - 1/2 pi r^2 → \frac{{1}}{{2}}\pi r^2
            - dx/d y → \frac{{dx}}{{dy}}


            IMPORTANT:
            - You may modify ONLY equations.
            - You must NOT change the meaning of normal text.

            ----------------------------------------------------------
            4. STRICT RULES
            ----------------------------------------------------------
            - Do NOT hallucinate full new equations.
            - Only restore equations that visibly appear in the text.
            - Do NOT summarize or rearrange text.
            - Keep equations in the exact same location as in the original.

            ----------------------------------------------------------
            Now translate the following text and restore all equations:

            ------------------
            {original_text}
            ------------------

            Output only the translated text (with restored LaTeX equations)."""
        )


        self.chat_model = init_chat_model(
            model_name,
            api_key=api_key,
            model_provider="google_genai"
        )

        # self.structured_model = self.chat_model.with_structured_output(
        #     Translation
        # )

        # self.chain = self.prompt_template | self.structured_model

    def translate(self, original_text: str) -> Translation:
        """Translate text using Gemini API"""

        translation = self.chat_model.invoke(
            self.prompt_template.format(original_text=original_text)
        )
        print(translation)
        return Translation(translated_text=translation.content)
