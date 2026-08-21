function ScanSummary({ result }) {
  return (
    <section className="summary-section">
      <div className="section-top">
        <div>
          <p className="eyebrow">SCAN RESULT</p>
          <h2>{result.application}</h2>
        </div>

        <div className="completion-status">
          <span className="status-dot"></span>
          Scan completed
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Files scanned</span>
          <strong>{result.scanned_file_count}</strong>
        </div>

        <div className="stat-card">
          <span className="stat-label">Supported files</span>
          <strong>{result.supported_file_count}</strong>
        </div>

        <div className="stat-card">
          <span className="stat-label">Evidence signals</span>
          <strong>{result.evidence_records.length}</strong>
        </div>

        <div className="stat-card">
          <span className="stat-label">AI assets discovered</span>
          <strong>{result.correlated_assets.length}</strong>
        </div>
      </div>
    </section>
  );
}

export default ScanSummary;