import { useRef, useEffect, useState } from "react";
import styles from "./PdfPreview.module.css";
export default function PdfPreview({ pdfDoc, page, pageCount, onChangePage }) {
  const canvasRef = useRef(null);

  const [pageInput, setPageInput] = useState(String(page));

  useEffect(() => {
    if (!pdfDoc) return;
    (async () => {
      if (page < 1 || page > pdfDoc.numPages) return;
      const p = await pdfDoc.getPage(page);
      const viewport = p.getViewport({ scale: 1.25 });
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      await p.render({ canvasContext: ctx, viewport }).promise;
    })();
  }, [pdfDoc, page]);

  // keep the input synced when page prop changes
  useEffect(() => {
    setPageInput(String(page));
  }, [page]);

  const handlePageInputKeyDown = (e) => {
    if (e.key !== "Enter") return;
    const n = Number(pageInput);
    if (!Number.isInteger(n)) return;
    const maxPage = pageCount || (pdfDoc ? pdfDoc.numPages : n);
    const newPage = Math.max(1, Math.min(n, maxPage));
    if (newPage !== page) onChangePage(newPage);
  };

  return (
    <div className={`${styles.box}`} style={{ flex: 1, height: "98vh", overflowY: "auto" }}>
      <h3>PDF Preview</h3>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <button disabled={page <= 1} onClick={() => onChangePage(page - 1)}>
          Prev
        </button>
        <span>
          Page {page} / {pageCount}
        </span>
        <button disabled={page >= pageCount} onClick={() => onChangePage(page + 1)}>
          Next
        </button>

        {/* Go-to-page input */}
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <label style={{ fontSize: 13 }}>Go to:</label>
          <input
            type="number"
            min={1}
            max={pageCount}
            value={pageInput}
            onChange={(e) => setPageInput(e.target.value)}
            onKeyDown={handlePageInputKeyDown}
            style={{ width: 72, padding: "4px 6px" }}
            aria-label="Go to page"
          />
        </div>
      </div>
      <canvas ref={canvasRef} style={{ marginTop: 8, border: "1px solid #ddd", maxWidth: "100%" }} />
    </div>
  );
}
