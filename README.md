## Running the Demo

This project ships with a sample multi-application environment for testing
AI asset discovery: `organization_environment/`, containing three services
with realistic AI usage patterns (source code, configuration, and
Terraform infrastructure).

### 1. Start the backend

\```bash
uvicorn app.api.main:app --reload
\```
Runs at `http://127.0.0.1:8000`.

### 2. Start the frontend

\```bash
cd frontend
npm install
npm run dev
\```

### Access the app

Once both servers are running, open:

**http://localhost:5173/**

This loads the AI Asset Discovery frontend, where you can run scans using
the demo applications listed above.

### 3. Run a discovery scan

On the "Run an asset scan" form, enter the **application name** and the
**directory path**, then click "Run discovery scan". Use one of the
following three demo applications:

| Application name               | Application directory (relative to project root)        |
| ------------------------------ | ------------------------------------------------------- |
| `customer-support-service`     | `organization_environment/customer-support-service`     |
| `document-processing-service`  | `organization_environment/document-processing-service`  |
| `recommendation-agent-service` | `organization_environment/recommendation-agent-service` |

> **Note:** The directory field currently requires the path resolved from
> wherever the backend process is running (typically the project root).
> If a relative path isn't recognized, use the full absolute path to the
> folder on your machine instead, e.g.
> `C:\path\to\project\organization_environment\customer-support-service`.

### 4. Expected results

- **customer-support-service** → 1 AI asset, status `DISCOVERED`
  (OpenAI / gpt-4o, evidence from source code + config + Terraform)
- **document-processing-service** → 1 AI asset, status `DISCOVERED`
  (Anthropic / claude-3, evidence from source code + config + Terraform)
- **recommendation-agent-service** → 1 AI asset, status `PENDING_REVIEW`
  (LangChain usage detected, but insufficient source-type diversity to
  reach full confidence — demonstrates the platform's evidence-based
  gating logic rather than accepting a single signal at face value)

Each result includes the underlying evidence records (file, line number,
matched signature, confidence weight) in the "Supporting Evidence" panel
below the asset inventory.
