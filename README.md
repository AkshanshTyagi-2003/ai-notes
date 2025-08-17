# AI Meeting Summarizer

A **FastAPI-based backend service** to upload, summarize, edit, and share meeting transcripts. Convert meeting notes into structured summaries and easily share via email.

---

## Features

- Upload transcript and get a `transcript_id`
- Summarize transcript with custom instructions
- Save/Edit generated summaries
- Share summaries via email
- One-click test for full workflow

---

## Installation

```bash
git clone https://github.com/AkshanshTyagi-2003/ai-notes.git
cd ai-notes
python -m venv venv
venv\Scripts\activate   # Windows
```
or
```bash
source venv/bin/activate # Linux/Mac
pip install -r requirements.txt
```
---
## Environment Variables 

Create a .env file:
```bash
SMTP_USER=your_email@example.com
SMTP_PASS=your_email_password
```
---


## API Endpoints

### 1. Upload Transcript
- POST /upload
- Request:

```bash
{
  "transcript_text": "Your meeting transcript here"
}
```
- Response
```bash
{
  "transcript_id": "uuid-string",
  "note": "Copy this transcript_id for summarizing."
}
```

### 2. Summarize Transcript
- POST /summarize
- Request:
```bash
{
  "transcript_id": "uuid-string",
  "instruction": "Summarize in bullet points for executives"
}
```
- Response
```bash
{
  "summary_id": "uuid-string",
  "summary_text": "Generated editable text",
  "structured": "Structured summary"
}
```

### 3. Save/Edit Summary
- PUT /summary
- Request:
```bash
{
  "summary_id": "uuid-string",
  "edited_text": "Updated summary"
}
```

- Response:
```bash
{
  "ok": true
}
```

### 4. Share Summary via Email
- POST /share
- Request:
```bash
{
  "summary_id": "uuid-string",
  "recipients": ["recipient@example.com"]
}
```
- Response:
```bash
{
  "ok": true,
  "message": "Email sent successfully to recipient@example.com"
}
```

### 5. One-Click Test
- POST /`test-all`
- Uploads a sample transcript, summarizes, edits, and shares it in one call. Useful for testing all functionalities.

---

## Authentication

All endpoints require headers:
```bash
x-username: akshanshtyagi
x-password: password123
```
---
