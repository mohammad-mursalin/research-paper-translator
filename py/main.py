import os
import re
import hashlib
import fitz  # PyMuPDF
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
import models

# Text Cleaning
def clean_extracted_text(text: str) -> str:
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\t+', ' ', text)

    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)

    while i < n:
        raw_line = lines[i]
        line = raw_line.strip()

        # handle blank lines
        if line == "":
            if not out or out[-1] != "":
                out.append("")
            i += 1
            continue

        # Dash with content merge
        m_dash_with_text = re.match(r'^[–—-]\s+(.*)$', line)
        if m_dash_with_text:
            content = m_dash_with_text.group(1).strip()
            if out:
                out[-1] = out[-1].rstrip() + " – " + content
            else:
                out.append("– " + content)
            i += 1
            continue

        # Dash-only line
        if re.match(r'^[–—-]\s*$', line):
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if out and j < n:
                next_line = lines[j].strip()
                prev = out.pop()
                out.append(prev.rstrip() + " – " + next_line)
                i = j + 1
                continue
            else:
                out.append("–")
                i += 1
                continue

        # Handle Bullets
        m_bullet = re.match(r'^[\.\*\u2022\u25E6\u2043]\s*(.*)$', line)
        if m_bullet:
            bullet_text = m_bullet.group(1).strip()
            out.append("• " + bullet_text)
            i += 1
            continue

        # Hyphen join
        if out and out[-1].rstrip().endswith("-"):
            prev = out.pop()
            merged = prev + line
            out.append(merged)
            i += 1
            continue

        # Continuation line
        if (
            out
            and re.match(r'^[a-z0-9]', line)
            and not re.search(r'[.?!:;]$', out[-1])
            and not out[-1].startswith("• ")
        ):
            out[-1] = out[-1] + " " + line
            i += 1
            continue

        # new line : eta default
        out.append(line)
        i += 1

    # Reconstruct
    result = "\n".join(out)

    # Cleanup
    result = re.sub(r'-\n(?=\w)', '', result)  # fix hyphen + newline
    result = re.sub(r'\s*[–—]\s*', ' – ', result)  # normalize dash spacing
    result = re.sub(r'[ \t]{2,}', ' ', result)  # collapse spaces
    result = re.sub(r'\n{3,}', '\n\n', result)  # collapse blank lines

    return result.strip()


# -----------------
# Environment & storage
load_dotenv()

PORT = int(os.getenv("PORT", "8000"))
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

# ---------------
# FastAPI setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------
# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------
# Models
class Metadata(BaseModel):
    file_id: str
    page_count: int


# ----------------
# PDF Text Extraction
def extract_text_from_page(page, cols: int):
    page_width = page.rect.width
    page_height = page.rect.height

    # thresholds
    header_y = page_height * 0.15
    footer_y = page_height * 0.85

    headers, footers, titles = [], [], []

    # blocks: (x0, y0, x1, y1, text, block_no, block_type)
    blocks = page.get_text("blocks", flags=0)
    if not blocks:
        return {"columns": []}

    blocks.sort(key=lambda b: (b[1], b[0]))  # top-to-bottom, left-to-right
    para_blocks = []

    for b in blocks:
        x0, y0, x1, y1, text, *_ = b
        text = text.strip()
        if not text:
            continue

        if y1 < header_y:  # header
            headers.append(clean_extracted_text(text))
            if len(text.split()) > 3 and text == text.upper():
                titles.append(clean_extracted_text(text))
        elif y0 > footer_y:  # footer
            footers.append(clean_extracted_text(text))
        else:  # main text
            para_blocks.append((x0, y0, text))

    # Single column
    if cols <= 1:
        para_blocks.sort(key=lambda t: t[1])
        joined_raw = "\n".join(t for _, __, t in para_blocks)
        cleaned = clean_extracted_text(joined_raw)
        return {
            "headers": headers,
            "titles": list(dict.fromkeys(titles)),
            "footers": footers,
            "columns": [cleaned],
        }

    # Multi-column
    col_width = page_width / cols
    col_items = [[] for _ in range(cols)]

    for x0, y0, text in para_blocks:
        col_idx = min(int(x0 // col_width), cols - 1)
        col_items[col_idx].append((y0, text))

    columns = []
    for items in col_items:
        items.sort(key=lambda t: t[0])
        col_raw = "\n".join(t for _, t in items)
        columns.append(clean_extracted_text(col_raw).strip())

    joined_text = "\n".join(c for c in columns if c)

    return {
        "headers": headers,
        "titles": list(dict.fromkeys(titles)),
        "footers": footers,
        "columns": columns,
        "joined_text": joined_text,
    }


# ---------------
# Routes
@app.get("/health")
async def health():
    return {"ok": True, "service": "py-fastapi"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        test_user = models.User(username="testuser", email="test@example.com", password="1234")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        users = db.query(models.User).all()
        return {"users": [{"id": u.id, "username": u.username, "email": u.email} for u in users]}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


@app.post("/pdf/ingest", response_model=Metadata)
async def ingest_pdf(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="empty_file")

    file_id = hashlib.sha256(content).hexdigest()[:16]
    pdf_path = os.path.join(STORAGE_DIR, f"{file_id}.pdf")

    with open(pdf_path, "wb") as f:
        f.write(content)

    try:
        with fitz.open(stream=content, filetype="pdf") as doc:
            page_count = doc.page_count
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"pdf_open_failed: {e}")

    return {"file_id": file_id, "page_count": page_count}


@app.get("/pdf/{file_id}/metadata", response_model=Metadata)
async def pdf_metadata(file_id: str):
    pdf_path = os.path.join(STORAGE_DIR, f"{file_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="not_found")

    with fitz.open(pdf_path) as doc:
        return {"file_id": file_id, "page_count": doc.page_count}


@app.post("/pdf/{file_id}/extract")
async def extract_pdf(
    file_id: str,
    page: int = Query(..., description="Page number to extract, starting from 1"),
    columns: int = Query(1, description="Number of columns on this page, default 1"),
):
    pdf_path = os.path.join(STORAGE_DIR, f"{file_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="not_found")

    try:
        with fitz.open(pdf_path) as doc:
            if page < 1 or page > doc.page_count:
                raise HTTPException(status_code=400, detail="invalid_page")
            page_obj = doc[page - 1]
            text = extract_text_from_page(page_obj, columns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"extract_failed: {e}")

    return {"file_id": file_id, "page": page, "text": text}


# ---------------
# Create tables
Base.metadata.create_all(bind=engine)
