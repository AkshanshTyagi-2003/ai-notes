// frontend/src/api.ts
export const API_BASE = "http://127.0.0.1:8000";

// -----------------------------
// API Endpoints with username/password headers
// -----------------------------
export async function uploadTranscript(
  text: string,
  username: string,
  password: string
) {
  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-username": username,
      "x-password": password,
    },
    body: JSON.stringify({ transcript_text: text }),
  });
  if (!response.ok) throw new Error(`Upload failed: ${response.statusText}`);
  return response.json();
}

export async function summarize(
  transcript_id: string,
  instruction: string,
  username: string,
  password: string
) {
  const response = await fetch(`${API_BASE}/summarize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-username": username,
      "x-password": password,
    },
    body: JSON.stringify({ transcript_id, instruction }),
  });
  if (!response.ok)
    throw new Error(`Summarize failed: ${response.statusText}`);
  return response.json();
}

export async function saveEdit(
  summary_id: string,
  edited_text: string,
  username: string,
  password: string
) {
  const response = await fetch(`${API_BASE}/summary`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "x-username": username,
      "x-password": password,
    },
    body: JSON.stringify({ summary_id, edited_text }),
  });
  if (!response.ok) throw new Error(`Save edit failed: ${response.statusText}`);
  return response.json();
}

export async function share(
  summary_id: string,
  recipients: string[],
  username: string,
  password: string
) {
  const response = await fetch(`${API_BASE}/share`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-username": username,
      "x-password": password,
    },
    body: JSON.stringify({ summary_id, recipients }),
  });
  if (!response.ok) throw new Error(`Share failed: ${response.statusText}`);
  return response.json();
}

export async function testAll(username: string, password: string) {
  const response = await fetch(`${API_BASE}/test-all`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-username": username,
      "x-password": password,
    },
  });
  if (!response.ok) throw new Error(`Test-all failed: ${response.statusText}`);
  return response.json();
}

// -----------------------------
// Default reviewer credentials
// -----------------------------
export const REVIEWER_CREDENTIALS = {
  username: "akshanshtyagi",
  password: "password123",
};

export default {
  uploadTranscript,
  summarize,
  saveEdit,
  share,
  testAll,
  REVIEWER_CREDENTIALS,
};
