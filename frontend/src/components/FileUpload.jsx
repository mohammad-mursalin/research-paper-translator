import styles from "./FileUpload.module.css"
function FileUpload({ onUpload }) {
  return (
    <label className={`${styles.fileUpload}`}>
      <span className={`${styles.uploadText}`}>
        Upload
        <br /> PDF
      </span>
      <i className={`fa-solid fa-upload ${styles.uploader}`}></i>
      <input
        type="file"
        accept="application/pdf"
        className="inputFile"
        onChange={onUpload}
      />
    </label>
  );
}
export default FileUpload;