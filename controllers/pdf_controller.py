from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from services.pdf_service import ingest_pdf_bytes, extract_pdf_by_page

router = APIRouter(
    prefix="/pdf",
    tags=["pdf"]
)


@router.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="empty_file")

    try:
        file_id, page_count = ingest_pdf_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"pdf_open_failed: {e}")

    return {"file_id": file_id, "page_count": page_count}


@router.get("/{file_id}/metadata")
async def pdf_metadata(file_id: str):
    try:
        # reuse extract_pdf_by_page to open PDF and get page count via PyMuPDF
        # open file and read page count
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


@router.get("/{file_id}/extract")
async def extract_pdf(file_id: str, page: int = Query(..., ge=1), columns: int = Query(1, ge=1)):
    try:
        text = extract_pdf_by_page(file_id, page, columns)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_page")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"extract_failed: {e}")

    return {"file_id": file_id, "page": page, "text": text}
