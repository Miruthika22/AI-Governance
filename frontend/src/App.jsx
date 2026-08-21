import { useState } from "react";

import Header from "./components/Header";
import ScanForm from "./components/ScanForm";
import ScanSummary from "./components/ScanSummary";
import AssetTable from "./components/AssetTable";
import EvidencePanel from "./components/EvidencePanel";

import "./App.css";


function App() {
  const [scanResult, setScanResult] = useState(null);

  return (
    <div className="app-shell">
      <Header />

      <main className="main-content">

        <section className="hero-section">
          <p className="eyebrow">
            AI GOVERNANCE PLATFORM
          </p>

          <h1>
            Discover AI assets across your applications.
          </h1>

          <p className="hero-description">
            Scan source code, configuration files, and infrastructure
            definitions to identify AI providers, models, and related
            evidence.
          </p>
        </section>

        <ScanForm
          onScanComplete={setScanResult}
        />

        {scanResult && (
          <div className="dashboard-results">

            <ScanSummary result={scanResult} />

            <AssetTable
              assets={scanResult.correlated_assets}
            />

            <EvidencePanel
              evidence={scanResult.evidence_records}
            />

          </div>
        )}

      </main>
    </div>
  );
}

export default App;