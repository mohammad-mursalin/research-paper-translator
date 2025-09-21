from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from services.pdf_service import PdfService

router = APIRouter(
    prefix="/pdf",
    tags=["pdf"]
)

pdf_service = PdfService()


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """
    Accept multipart/form-data with key 'file' (PDF).
    Returns { file_id, page_count }.
    """
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="empty_file")

    try:
        file_id, page_count = pdf_service.ingest_pdf_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest PDF: {e}")

    return {"file_id": file_id, "page_count": page_count}


@router.get("/{file_id}/metadata")
async def pdf_metadata(file_id: str):
    try:
        import fitz
        from os import path
        storage = __import__('os').getenv('STORAGE_DIR', './storage')
        pdf_path = path.join(storage, f"{file_id}.pdf")
        if not path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="not_found")
        with fitz.open(pdf_path) as doc:
            return {"file_id": file_id, "page_count": doc.page_count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{file_id}/extract")
async def extract(
    file_id: str,
    page: int = Query(..., description="Page number (1-based)"),
    columns: int = Query(1, description="Number of text columns")
):
    """
    Extract text for file_id and page.
    Query params: ?page=1&columns=1
    Returns structured extraction (headers, titles, footers, columns, joined_text)
    """
    try:
        extraction = pdf_service.extract_pdf_by_page(file_id=file_id, page=page, columns=columns)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PDF not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    return {"file_id": file_id, "page": page, "text": extraction}
