import { useState } from "react";
import { runScan } from "../services/api";

function ScanForm({ onScanComplete }) {
  const [application, setApplication] = useState("demo-app");
  const [rootDir, setRootDir] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!application.trim() || !rootDir.trim()) {
      setError("Please provide both application name and directory path.");
      return;
    }

    try {
      setLoading(true);

      const result = await runScan(application, rootDir);

      onScanComplete(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="scan-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">DISCOVERY</p>
          <h2>Run an asset scan</h2>
          <p className="section-description">
            Select an application directory to identify AI providers,
            models, configuration signals, and infrastructure evidence.
          </p>
        </div>
      </div>

      <form className="scan-form" onSubmit={handleSubmit}>

        <div className="form-group">
          <label htmlFor="application">
            Application name
          </label>

          <input
            id="application"
            type="text"
            value={application}
            onChange={(e) => setApplication(e.target.value)}
            placeholder="e.g. demo-app"
          />
        </div>

        <div className="form-group">
          <label htmlFor="rootDir">
            Application directory
          </label>

          <input
            id="rootDir"
            type="text"
            value={rootDir}
            onChange={(e) => setRootDir(e.target.value)}
            placeholder="e.g. C:\Projects\my-application"
          />

          <span className="input-hint">
            Enter the absolute path of the application you want to scan.
          </span>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <button
          type="submit"
          className="scan-button"
          disabled={loading}
        >
          {loading ? "Scanning..." : "Run discovery scan"}
        </button>

      </form>
    </section>
  );
}

export default ScanForm;