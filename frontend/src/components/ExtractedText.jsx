import styles from "./ExtractedText.module.css";
import { useEffect } from "react";

export default function ExtractedText({ extractedText, extractedTextJoin, translation, translating }) {

  useEffect(() => {
    if (!window.MathJax) {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
      script.async = true;
      script.onload = () => {
        window.MathJax.typesetPromise();
      };
      document.head.appendChild(script);
    } else {
      window.MathJax.typesetPromise();
    }
  }, [translation]);

  if ((!extractedText || extractedText.length === 0) && !translation && !translating) return null;

  return (
    <div style={{ flex: 1 }} className={`${styles.box}`}>
      <h3>Extracted Text</h3>

      {extractedText && extractedText.length > 0 && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            maxHeight: "40vh",
            overflowY: "auto",
            marginBottom: "16px",
          }}
        >
          {extractedText.map((block, idx) => (
            <div
              key={idx}
              style={{
                padding: "12px",
                border: "1px solid #ccc",
                borderRadius: "8px",
                background: "#f9f9f9",
                fontFamily: "monospace",
                whiteSpace: "pre-wrap",
              }}
            >
              {block}
            </div>
          ))}
        </div>
      )}

      {/* Show inline translating banner where translated text will appear */}
      {translating && (
        <div style={{
          padding: "12px",
          border: "1px solid #4a90e2",
          borderRadius: 8,
          background: "linear-gradient(90deg,#007bff,#00aaff)",
          color: "#fff",
          display: "flex",
          gap: 12,
          alignItems: "center",
          minHeight: 80,
          marginBottom: 12,
          whiteSpace: "normal"
        }}>
          <svg width="28" height="28" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="6" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeDasharray="28" strokeDashoffset="20">
              <animateTransform attributeName="transform" type="rotate" from="0 8 8" to="360 8 8" dur="1s" repeatCount="indefinite" />
            </circle>
          </svg>
          <div>
            <div style={{ fontWeight: 700 }}>Translating page — please wait</div>
            <div style={{ fontSize: 13, opacity: 0.95 }}>The translated text will appear here once ready.</div>
          </div>
        </div>
      )}

      {translation && (
        <div
          style={{
            padding: "12px",
            border: "1px solid #4a90e2",
            borderRadius: "8px",
            background: "#d0e7ff",
            whiteSpace: "pre-wrap",
          }}
        >
          <strong>Translated Text:</strong>
          <p>{translation}</p>
        </div>
      )}
    </div>
  );
}
