function AssetTable({ assets }) {
  if (!assets || assets.length === 0) {
    return (
      <section className="results-card asset-inventory-section">
        <div className="section-title">
          <div>
            <p className="eyebrow">AI ASSET INVENTORY</p>
            <h2>Identified AI assets</h2>
            <p className="section-description">
              No correlated AI assets were identified during this scan.
            </p>
          </div>
        </div>

        <div className="empty-state">
          No AI assets were discovered during this scan.
        </div>
      </section>
    );
  }

  return (
    <section className="results-card asset-inventory-section">
      <div className="section-title">
        <div>
          <p className="eyebrow">AI ASSET INVENTORY</p>
          <h2>Identified AI assets</h2>

          <p className="section-description asset-description">
            AI systems identified from correlated discovery evidence.
          </p>
        </div>

        <span className="asset-count">
          {assets.length} found
        </span>
      </div>

      <div className="asset-grid">
        {assets.map((asset) => {
          const confidence = Math.round(asset.confidence * 100);

          return (
            <article
              className="asset-card"
              key={asset.id}
            >
              <div className="asset-card-top">
                <div>
                  <p className="asset-provider">
                    {asset.provider}
                  </p>

                  <h3 className="asset-model">
                    {asset.model || "Model not resolved"}
                  </h3>
                </div>

                <span
                  className={`asset-status ${
                    asset.status === "discovered"
                      ? "status-discovered"
                      : "status-pending"
                  }`}
                >
                  <span className="asset-status-dot"></span>

                  {asset.status.replace("_", " ")}
                </span>
              </div>

              <div className="asset-type">
                {asset.ai_type}
              </div>

              <div className="asset-confidence">
                <div className="asset-confidence-header">
                  <span>Confidence</span>
                  <strong>{confidence}%</strong>
                </div>

                <div className="asset-confidence-track">
                  <div
                    className="asset-confidence-fill"
                    style={{
                      width: `${confidence}%`,
                    }}
                  />
                </div>
              </div>

              <div className="asset-divider"></div>

              <div className="asset-meta-grid">
                <div>
                  <span className="asset-meta-label">
                    AI Type
                  </span>

                  <strong>
                    {asset.ai_type || "Not classified"}
                  </strong>
                </div>

                <div>
                  <span className="asset-meta-label">
                    Status
                  </span>

                  <strong className="asset-meta-status">
                    {asset.status.replace("_", " ")}
                  </strong>
                </div>
              </div>

              <button
                type="button"
                className="asset-details-button"
              >
                View asset details
                <span>→</span>
              </button>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default AssetTable;