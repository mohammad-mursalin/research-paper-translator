import styles from "./LandingPage.module.css";

function LandingPage({ onTryNow }) {
  return (
    <section id="section1" className={`${styles.landingPage}`}>
      <div className={`${styles.text}`}>
        <h4>GLOBAL RESEARCH IN</h4>
        <h1>BANGLA</h1>
        <p>
          Translating academic PDFs into Bangla to empower students, teachers,
          and researchers nationwide.
        </p>
        <button className={`${styles.btn2}`} onClick={onTryNow}>
          TRY IT NOW
        </button>
      </div>
      <div className={`${styles.right}`}>
        <i className={`fa-solid fa-file-pdf ${styles.pdflogo}`}></i>
        <i className={`fa-solid fa-pencil ${styles.rotatePencil}`}></i>
      </div>
      <div className={`${styles.side}`}>
        <div className={`${styles.side1}`}>
          <div className={`${styles.searchicon}`}>
            <a href="#" className="icon1">
              <i className="fa-solid fa-earth-asia"></i>
            </a>
          </div>
          <h4>TRANSLATE</h4>
        </div>
        <div className={`${styles.side2}`}>
          <h4>ANYTHING - 0</h4>
        </div>
      </div>
      <div className={`${styles.version}`}>--version 0.0:MVA</div>
      <div className="circle"></div>
    </section>
  );
}

export default LandingPage;
