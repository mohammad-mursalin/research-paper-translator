import os
import re
import hashlib
import tempfile
import fitz  # PyMuPDF

DEFAULT_STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")


def _get_storage_dir():
    storage = os.getenv("STORAGE_DIR", "./storage")
    os.makedirs(storage, exist_ok=True)
    return storage


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
        m_dash_with_text = re.match(r'^[\u2013\u2014-]\s+(.*)$', line)
        if m_dash_with_text:
            content = m_dash_with_text.group(1).strip()
            if out:
                out[-1] = out[-1].rstrip() + " \u2013 " + content
            else:
                out.append("\u2013 " + content)
            i += 1
            continue

        # Dash-only line
        if re.match(r'^[\u2013\u2014-]\s*$', line):
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if out and j < n:
                next_line = lines[j].strip()
                prev = out.pop()
                out.append(prev.rstrip() + " \u2013 " + next_line)
                i = j + 1
                continue
            else:
                out.append("\u2013")
                i += 1
                continue

        # Handle Bullets
        m_bullet = re.match(r'^[\.\*\u2022\u25E6\u2043]\s*(.*)$', line)
        if m_bullet:
            bullet_text = m_bullet.group(1).strip()
            out.append("\u2022 " + bullet_text)
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
            and not out[-1].startswith("\u2022 ")
        ):
            out[-1] = out[-1] + " " + line
            i += 1
            continue

        # new line
        out.append(line)
        i += 1

    # Reconstruct
    result = "\n".join(out)

    # Cleanup
    result = re.sub(r'-\n(?=\w)', '', result)  # fix hyphen + newline
    result = re.sub(r'\s*[\u2013\u2014]\s*', ' \u2013 ', result)  # normalize dash spacing
    result = re.sub(r'[ \t]{2,}', ' ', result)  # collapse spaces
    result = re.sub(r'\n{3,}', '\n\n', result)  # collapse blank lines

    return result.strip()


class PdfService:
    def __init__(self, storage_dir: str = DEFAULT_STORAGE_DIR):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _file_path(self, file_id: str):
        return os.path.join(self.storage_dir, f"{file_id}.pdf")

    def ingest_pdf_bytes(self, file_bytes: bytes):
        """
        Save PDF bytes to storage, return (file_id, page_count).
        file_id is SHA256 hex digest of content.
        """
        file_id = hashlib.sha256(file_bytes).hexdigest()
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf", dir=self.storage_dir)
        try:
            with os.fdopen(tmp_fd, "wb") as f:
                f.write(file_bytes)
            final_path = self._file_path(file_id)
            os.replace(tmp_path, final_path)
            # read page count
            doc = fitz.open(final_path)
            page_count = doc.page_count
            doc.close()
            return file_id, page_count
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def extract_pdf_by_page(self, file_id: str, page: int, columns: int = 1):
        """
        Extract text for a specific page (1-based page index).
        Returns a dict:
          { headers: [], titles: [], footers: [], columns: [ [...], ... ], joined_text: "..." }
        """
        path = self._file_path(file_id)
        if not os.path.exists(path):
            raise FileNotFoundError("PDF not found")

        doc = fitz.open(path)
        try:
            # page index in PyMuPDF is 0-based
            page_idx = int(page) - 1
            if page_idx < 0 or page_idx >= doc.page_count:
                raise ValueError("page out of range")
            pg = doc.load_page(page_idx)

            # Basic extraction: plain text and simple column split
            joined_text = pg.get_text("text") or ""
            # naive column split by vertical slices is complex; for now return single column
            columns_text = [joined_text]

            # simple placeholders for headers/titles/footers
            headers = []
            titles = []
            footers = []

            # basic cleaning: normalize newlines
            joined_text = "\n".join([line.rstrip() for line in joined_text.splitlines() if line.strip()])

            return {
                "headers": headers,
                "titles": titles,
                "footers": footers,
                "columns": columns_text,
                "joined_text": joined_text,
            }
        finally:
            doc.close()
