import os
import re
import hashlib

# Defer heavy imports (PyMuPDF) to function scope so module import doesn't fail if
# optional deps are missing during static checks.


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


def ingest_pdf_bytes(content: bytes):
    """Save PDF bytes to storage and return (file_id, page_count).

    This function imports PyMuPDF lazily so the module can be imported even if
    PyMuPDF is not installed yet.
    """
    file_id = hashlib.sha256(content).hexdigest()[:16]
    pdf_path = os.path.join(_get_storage_dir(), f"{file_id}.pdf")

    # atomic write
    with open(pdf_path, "wb") as f:
        f.write(content)

    try:
        import fitz  # PyMuPDF

        with fitz.open(stream=content, filetype="pdf") as doc:
            page_count = doc.page_count
    except Exception as e:
        # remove the file if it isn't a valid PDF
        try:
            os.remove(pdf_path)
        except Exception:
            pass
        raise

    return file_id, page_count


def extract_pdf_by_page(file_id: str, page: int, columns: int = 1):
    pdf_path = os.path.join(_get_storage_dir(), f"{file_id}.pdf")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("not_found")

    try:
        import fitz  # PyMuPDF

        with fitz.open(pdf_path) as doc:
            if page < 1 or page > doc.page_count:
                raise ValueError("invalid_page")
            page_obj = doc[page - 1]
            # copy of the extraction logic using page.get_text('blocks')
            page_width = page_obj.rect.width
            page_height = page_obj.rect.height

            header_y = page_height * 0.15
            footer_y = page_height * 0.85

            headers, footers, titles = [], [], []
            blocks = page_obj.get_text("blocks", flags=0)
            if not blocks:
                return {"columns": []}

            blocks.sort(key=lambda b: (b[1], b[0]))
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

            if columns <= 1:
                para_blocks.sort(key=lambda t: t[1])
                joined_raw = "\n".join(t for _, __, t in para_blocks)
                cleaned = clean_extracted_text(joined_raw)
                return {
                    "headers": headers,
                    "titles": list(dict.fromkeys(titles)),
                    "footers": footers,
                    "columns": [cleaned],
                }

            col_width = page_width / columns
            col_items = [[] for _ in range(columns)]

            for x0, y0, text in para_blocks:
                col_idx = min(int(x0 // col_width), columns - 1)
                col_items[col_idx].append((y0, text))

            columns_out = []
            for items in col_items:
                items.sort(key=lambda t: t[0])
                col_raw = "\n".join(t for _, t in items)
                columns_out.append(clean_extracted_text(col_raw).strip())

            joined_text = "\n".join(c for c in columns_out if c)

            return {
                "headers": headers,
                "titles": list(dict.fromkeys(titles)),
                "footers": footers,
                "columns": columns_out,
                "joined_text": joined_text,
            }
    except FileNotFoundError:
        raise
    except Exception as e:
        raise
