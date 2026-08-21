function EvidencePanel({ evidence }) {
  if (!evidence || evidence.length === 0) {
    return null;
  }

  return (
    <section className="results-card evidence-section">
      <div className="section-title">
        <div>
          <p className="eyebrow">SUPPORTING EVIDENCE</p>
          <h2>Discovery signals</h2>
        </div>

        <span className="asset-count">
          {evidence.length} signals
        </span>
      </div>

      <div className="evidence-list">
        {evidence.map((item) => (
          <article
            className="evidence-item"
            key={item.id}
          >
            <div className="evidence-source">
              <span className="source-tag">
                {item.source_type.replace("_", " ")}
              </span>

              <span className="signal-tag">
                {item.signal_type}
              </span>
            </div>

            <div className="evidence-details">
              <h3>
                {item.provider || "Unknown provider"}
                {item.model && ` · ${item.model}`}
              </h3>

              <p className="file-path">
                {item.source_path}
                {item.line_number &&
                  ` : line ${item.line_number}`}
              </p>

              <div className="evidence-meta">
                <span>
                  AI type: {item.ai_type || "Unknown"}
                </span>

                <span>
                  Confidence:{" "}
                  {Math.round(
                    item.confidence_weight * 100
                  )}%
                </span>

                <span>
                  Specificity: {item.specificity}
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default EvidencePanel;