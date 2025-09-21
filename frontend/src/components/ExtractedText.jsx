import styles from "./ExtractedText.module.css";

export default function ExtractedText({ extractedText, extractedTextJoin, translation }) {
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
