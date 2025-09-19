from fastapi import FastAPI
from controllers.gemini_translation_controller import router as gemini_router
from controllers.pdf_controller import router as pdf_router

app = FastAPI()
app.include_router(gemini_router)
app.include_router(pdf_router)
