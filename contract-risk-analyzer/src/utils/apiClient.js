const API_BASE_URL = "/api";

export async function uploadContract(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to upload contract document.");
  }

  return response.json();
}

export async function getAnalysisStatus(analysisId) {
  const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/status`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to fetch analysis status.");
  }
  return response.json();
}

export async function getAnalysisResult(analysisId) {
  const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/result`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to fetch analysis report.");
  }
  return response.json();
}

export async function getAnalysisHistory() {
  const response = await fetch(`${API_BASE_URL}/history`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to fetch analysis history.");
  }
  return response.json();
}

export async function postFollowupChat(analysisId, message) {
  const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to get chat response.");
  }
  return response.json();
}
