import { useRef, useEffect } from "react";
import styles from "./PdfPreview.module.css";
export default function PdfPreview({ pdfDoc, page, pageCount, onChangePage }) {
  const canvasRef = useRef(null);

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
      </div>
      <canvas ref={canvasRef} style={{ marginTop: 8, border: "1px solid #ddd", maxWidth: "100%" }} />
    </div>
  );
}
