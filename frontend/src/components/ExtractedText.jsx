import styles from "./ExtractedText.module.css";

export default function ExtractedText({ extractedText }) {
  if (!extractedText || extractedText.length === 0) return null;

  return (
    <div style={{ flex: 1 }} className={`${styles.box}`}>
      <h3>Extracted Text</h3>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          maxHeight: "80vh",
          overflowY: "auto",
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
    </div>
  );
}
