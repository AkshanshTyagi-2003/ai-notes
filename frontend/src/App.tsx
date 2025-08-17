// frontend/src/App.tsx
import React, { useState } from "react";
import api from "./api";
import "./App.css";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [transcript, setTranscript] = useState("");
  const [instruction, setInstruction] = useState("");
  const [transcriptId, setTranscriptId] = useState("");
  const [summaryId, setSummaryId] = useState("");
  const [summary, setSummary] = useState("");
  const [recipients, setRecipients] = useState("");
  const [loading, setLoading] = useState(false);

  const HARDCODED_USERNAME = "akshanshtyagi";
  const HARDCODED_PASSWORD = "password123";

  // Copy to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert(`Copied "${text}" to clipboard!`);
  };

  // Login check
  const handleLogin = () => {
    if (username === HARDCODED_USERNAME && password === HARDCODED_PASSWORD) {
      alert("Login successful! You can now access all functionalities.");
    } else {
      alert("Invalid credentials. Use the copy button to fill them correctly.");
    }
  };

  // Upload transcript
  const handleUpload = async () => {
    try {
      setLoading(true);
      const res = await api.uploadTranscript(transcript, username, password);
      setTranscriptId(res.transcript_id);
      alert("Transcript uploaded successfully!");
    } catch (err: any) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Summarize
  const handleSummarize = async () => {
    if (!transcriptId) {
      alert("Upload transcript first");
      return;
    }
    try {
      setLoading(true);
      const res = await api.summarize(transcriptId, instruction, username, password);
      setSummaryId(res.summary_id);
      setSummary(res.summary_text);
    } catch (err: any) {
      alert("Summarization failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Save edit
  const handleSaveEdit = async () => {
    if (!summaryId) {
      alert("No summary to edit");
      return;
    }
    try {
      setLoading(true);
      await api.saveEdit(summaryId, summary, username, password);
      alert("Summary saved successfully!");
    } catch (err: any) {
      alert("Save failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Share
  const handleShare = async () => {
    if (!summaryId) {
      alert("No summary to share");
      return;
    }
    try {
      setLoading(true);
      const emails = recipients.split(",").map((e) => e.trim());
      await api.share(summaryId, emails, username, password);
      alert("Summary shared successfully!");
    } catch (err: any) {
      alert("Share failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>AI Meeting Notes</h1>

      {/* Username */}
      <div style={{ position: "relative", marginBottom: 12 }}>
        <input
          style={styles.input}
          placeholder="x-username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <div style={styles.copyBox}>
          <span>{HARDCODED_USERNAME}</span>
          <button style={styles.copyButton} onClick={() => copyToClipboard(HARDCODED_USERNAME)}>
            Copy
          </button>
        </div>
      </div>

      {/* Password */}
      <div style={{ position: "relative", marginBottom: 12 }}>
        <input
          type="password"
          style={styles.input}
          placeholder="x-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <div style={styles.copyBox}>
          <span>{HARDCODED_PASSWORD}</span>
          <button style={styles.copyButton} onClick={() => copyToClipboard(HARDCODED_PASSWORD)}>
            Copy
          </button>
        </div>
      </div>

      <button style={styles.button} onClick={handleLogin}>
        Login
      </button>

      {/* Transcript Section */}
      <textarea
        style={styles.textarea}
        placeholder="Paste transcript here..."
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
      />
      <button style={styles.button} onClick={handleUpload} disabled={loading}>
        Upload Transcript
      </button>

      <input
        style={styles.input}
        placeholder="Enter instruction (e.g. summarize in bullet points)"
        value={instruction}
        onChange={(e) => setInstruction(e.target.value)}
      />
      <button style={styles.button} onClick={handleSummarize} disabled={loading}>
        Generate Summary
      </button>

      {summary && (
        <>
          <textarea
            style={styles.textarea}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
          />
          <button style={styles.button} onClick={handleSaveEdit} disabled={loading}>
            Save Edited Summary
          </button>

          <input
            style={styles.input}
            placeholder="Recipients (comma separated emails)"
            value={recipients}
            onChange={(e) => setRecipients(e.target.value)}
          />
          <button style={styles.button} onClick={handleShare} disabled={loading}>
            Share Summary
          </button>
        </>
      )}
    </div>
  );
}

// Styles
const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: "700px",
    margin: "40px auto",
    padding: "20px",
    borderRadius: "10px",
    boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
    fontFamily: "Arial, sans-serif",
    background: "#fdfdfd",
  },
  heading: {
    textAlign: "center",
    marginBottom: "20px",
    color: "#333",
  },
  textarea: {
    width: "100%",
    height: "120px",
    marginBottom: "12px",
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "14px",
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "14px",
  },
  button: {
    display: "block",
    width: "100%",
    padding: "12px",
    marginBottom: "12px",
    borderRadius: "6px",
    border: "none",
    background: "#4CAF50",
    color: "white",
    fontSize: "16px",
    cursor: "pointer",
  },
  copyBox: {
    position: "absolute",
    right: 0,
    top: 0,
    display: "flex",
    alignItems: "center",
    background: "#f0f0f0",
    padding: "0 8px",
    borderRadius: "0 6px 6px 0",
    height: "100%",
  },
  copyButton: {
    marginLeft: "6px",
    padding: "2px 6px",
    fontSize: "12px",
    cursor: "pointer",
  },
};

export default App;
