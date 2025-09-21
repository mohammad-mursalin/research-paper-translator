import { useState, useEffect } from "react";
import * as pdfjsLib from "pdfjs-dist";
import "./pdfWorker";
import axios from "axios";
import ScrollReveal from "scrollreveal";

import LandingPage from "./components/LandingPage";
import FileUpload from "./components/FileUpload";
import PdfPreview from "./components/PdfPreview";
import ExtractedText from "./components/ExtractedText";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [localPdf, setLocalPdf] = useState(null);
  const [pdfDoc, setPdfDoc] = useState(null);
  const [pageCount, setPageCount] = useState(0);
  const [page, setPage] = useState(1);
  const [fileId, setFileId] = useState(null);
  const [columns, setColumns] = useState(1);
  const [extractedText, setExtractedText] = useState([]);
  const [extractedTextJoin, setExtractedTextJoin] = useState("");
  const [showExtraction, setShowExtraction] = useState(false);
  const [translation, setTranslation] = useState(null);
  const [uploading, setUploading] = useState(false);

  // ScrollReveal animations
  useEffect(() => {
    const sr = ScrollReveal({
      origin: "top",
      distance: "60px",
      duration: 2500,
      delay: 300,
      reset: false,
    });

    sr.reveal(".text, .footer");
    sr.reveal(".home__dish", {
      delay: 500,
      distance: "100px",
      origin: "bottom",
    });
    sr.reveal(".rotatePencil", {
      origin: "top",
      distance: "100px",
      duration: 1500,
      delay: 1200,
      rotate: { x: 0, y: 0, z: -45 },
    });
    sr.reveal(".version", { origin: "bottom", delay: 1600, interval: 100 });
    sr.reveal(".pdflogo", { origin: "right", distance: "100px" });
  }, []);

  // Load PDF for preview
  useEffect(() => {
    if (!localPdf) return;
    (async () => {
      const doc = await pdfjsLib.getDocument({ data: localPdf }).promise;
      setPdfDoc(doc);
      setPage(1);
      setPageCount(doc.numPages);
    })();
  }, [localPdf]);

  // Handle PDF file upload
  const onFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const arrBuf = await file.arrayBuffer();
    setLocalPdf(arrBuf);

    const form = new FormData();
    form.append("file", file);
    setUploading(true);
    try {
      const r = await axios.post(`${API_BASE}/pdf/ingest`, form);
      setFileId(r.data.file_id);
      setPageCount(r.data.page_count);
      setPage(1);
      setExtractedText([]);
      setExtractedTextJoin("");
    } finally {
      setUploading(false);
    }
  };

  // Extract text for current page
  const extractText = async (currentPage = page) => {
    if (!fileId) return;

    try {
      const r = await axios.post(`${API_BASE}/pdf/${fileId}/extract`, null, {
        params: { page: currentPage, columns },
      });
      setExtractedText(r.data.text.columns);
      setExtractedTextJoin(r.data.text.joined_text);
      setTranslation(null);
    } catch (err) {
      console.error("Text extraction failed:", err);
      alert("Extraction failed. Check console for details.");
    }
  };

  // Translate extracted text
  const translateText = async () => {
    if (!fileId || !page) return;

    try {
      const r = await axios.post(`${API_BASE}/gemini/translate`, null, {
        params: { file_id: fileId, page, columns },
      });
      setTranslation(
        r.data.translated_text ||
          r.data.translatedText ||
          r.data.translated ||
          r.data
      );console.log(r.data.translated_text);
    } catch (err) {
      console.error("Translation failed:", err);
      alert("Translation failed. Check console for details.");
    }
  };

  // Change page and auto-extract text
  const changePage = async (newPage) => {
    if (newPage < 1 || newPage > pageCount) return;
    setPage(newPage);
    setExtractedText([]);
    setExtractedTextJoin("");
    await extractText(newPage);
  };

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "24px auto",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      <LandingPage onTryNow={() => setShowExtraction(true)} />

      <section
        id="extraction"
        className={`extraction ${showExtraction ? "show" : ""}`}
      >
        {!fileId && (
          <div className="promo">
            <h1 className="slide-text">
              Bridging the World of Research to Bangla
            </h1>
            <h2>Feel Free To Upload</h2>
          </div>
        )}

        <FileUpload onUpload={onFile} />

        {fileId && (
          <div style={{ marginTop: 16 }}>
            <label>
              Columns:
              <input
                type="number"
                min={1}
                value={columns}
                onChange={(e) => setColumns(Number(e.target.value))}
                style={{ marginLeft: 8, width: 60 }}
              />
            </label>
            <button onClick={() => extractText()} style={{ marginLeft: 8 }}>
              Extract Text
            </button>
            <button
              onClick={() => translateText()}
              style={{ marginLeft: 8 }}
              disabled={!extractedTextJoin}
            >
              Translate Text
            </button>

            <section
              style={{ display: "flex", gap: "24px", marginTop: "16px" }}
            >
              <PdfPreview
                pdfDoc={pdfDoc}
                page={page}
                pageCount={pageCount}
                onChangePage={changePage}
              />
              <ExtractedText
                extractedText={extractedText}
                extractedTextJoin={extractedTextJoin}
                translation={translation}
              />
            </section>
          </div>
        )}
      </section>
    </div>
  );
}
