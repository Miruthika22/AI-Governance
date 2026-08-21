const API_BASE_URL = "http://127.0.0.1:8000";


export async function runScan(application, rootDir) {
  try {
    const response = await fetch(`${API_BASE_URL}/scan`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        application: application,
        root_dir: rootDir,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to run discovery scan."
      );
    }

    return data;

  } catch (error) {
    throw error;
  }
}


export async function checkHealth() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/health`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Backend is not available."
      );
    }

    return data;

  } catch (error) {
    throw error;
  }
}