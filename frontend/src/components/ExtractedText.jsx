import styles from "./ExtractedText.module.css";
import { useEffect } from "react";

export default function ExtractedText({ extractedText, extractedTextJoin, translation }) {

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

  if ((!extractedText || extractedText.length === 0) && !translation) return null;

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
