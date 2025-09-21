from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from controllers.gemini_translation_controller import router as gemini_router
from controllers.pdf_controller import router as pdf_router
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(gemini_router)
app.include_router(pdf_router)

@app.get("/health")
async def health():
    """Health check; reports whether GEMINI_API_KEY is configured (boolean) without exposing the value."""
    return {"ok": True, "gemini_key_set": bool(os.getenv("GEMINI_API_KEY"))}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000", "http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)