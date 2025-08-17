from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
import uuid
import os

from models import UploadRequest, SummarizeRequest, SaveEditRequest, ShareRequest, SummaryResponse
from llm import generate_summary
from emailer import send_email

# -----------------------------
# In-memory storage
# -----------------------------
TRANSCRIPTS = {}
SUMMARIES = {}

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    title="AI Meeting Summarizer",
    description="""
**Instructions for single actions**:

1. **Upload Transcript**: Paste your transcript and click 'Try it out'. Copy the `transcript_id` from the response.
2. **Summarize Transcript**: Paste the copied `transcript_id` in the input. Add any instruction (e.g., 'Summarize in bullet points') and click 'Try it out'. Copy the `summary_id` from the response.
3. **Save/Edit Summary**: Paste the copied `summary_id` and edited text. Click 'Try it out' to save changes.
4. **Share Summary**: Paste the copied `summary_id` and recipient emails. Click 'Try it out' to send email.
"""
)

# -----------------------------
# Predefined credentials
# -----------------------------
PREDEFINED_USERNAME = "akshanshtyagi"
PREDEFINED_PASSWORD = "password123"

# -----------------------------
# Header-based authentication
# -----------------------------
def verify_auth(
    x_username: str = Header(default=PREDEFINED_USERNAME, description="Predefined username for API access"),
    x_password: str = Header(default=PREDEFINED_PASSWORD, description="Predefined password for API access")
):
    if x_username != PREDEFINED_USERNAME or x_password != PREDEFINED_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return True

# -----------------------------
# Upload transcript
# -----------------------------
@app.post("/upload", summary="Upload Transcript", description="Paste your transcript. After uploading, copy the `transcript_id` for use in Summarize endpoint.")
def upload(req: UploadRequest, auth: bool = Depends(verify_auth)):
    transcript_id = str(uuid.uuid4())
    transcript = {"id": transcript_id, "text": req.transcript_text}
    TRANSCRIPTS[transcript_id] = transcript
    return {"transcript_id": transcript_id, "note": "Copy this transcript_id for single summarize."}

# -----------------------------
# Summarize transcript
# -----------------------------
@app.post("/summarize", response_model=SummaryResponse, summary="Summarize Transcript", description="Paste the copied `transcript_id` and add any instruction. Copy the `summary_id` from the response for saving or sharing.")
def summarize(req: SummarizeRequest, auth: bool = Depends(verify_auth)):
    transcript = TRANSCRIPTS.get(req.transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    structured, editable_text = generate_summary(transcript["text"], req.instruction)

    summary_id = str(uuid.uuid4())
    summary = {
        "id": summary_id,
        "transcript_id": transcript["id"],
        "structured": structured,
        "editable_text": editable_text,
        "generated_text": editable_text
    }
    SUMMARIES[summary_id] = summary

    return SummaryResponse(
        summary_id=summary_id,
        summary_text=editable_text,
        structured=structured
    )

# -----------------------------
# Save/Edit summary
# -----------------------------
@app.put("/summary", summary="Save/Edit Summary", description="Paste the copied `summary_id` and edit the text. Click Try it out to save changes.")
def save_edit(req: SaveEditRequest, auth: bool = Depends(verify_auth)):
    summary = SUMMARIES.get(req.summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    summary["editable_text"] = req.edited_text
    return {"ok": True}

# -----------------------------
# Share summary via email
# -----------------------------
@app.post("/share", summary="Share Summary", description="Paste the copied `summary_id` and recipient emails. Click Try it out to share the summary via email.")
def share(req: ShareRequest, auth: bool = Depends(verify_auth)):
    summary = SUMMARIES.get(req.summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    try:
        send_email(
            subject="Meeting Summary",
            body=summary["editable_text"],
            recipients=req.recipients
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    return {"ok": True, "message": f"Email sent successfully to {', '.join(req.recipients)}"}

# -----------------------------
# One-click test endpoint
# -----------------------------
@app.post("/test-all", summary="One-Click Test", description="Uploads sample transcript, summarizes, edits, and shares it. Used for testing all functionalities in one click.")
def test_all(auth: bool = Depends(verify_auth)):
    sample_text = "This is a sample meeting transcript. Discuss project deadlines and assign tasks."
    transcript_id = str(uuid.uuid4())
    transcript = {"id": transcript_id, "text": sample_text}
    TRANSCRIPTS[transcript_id] = transcript

    structured, editable_text = generate_summary(
        transcript["text"], "Summarize the meeting into clear sections with action items."
    )

    summary_id = str(uuid.uuid4())
    summary = {
        "id": summary_id,
        "transcript_id": transcript_id,
        "structured": structured,
        "editable_text": editable_text,
        "generated_text": editable_text
    }
    SUMMARIES[summary_id] = summary

    # Edit the summary
    edited_text = "# Updated Meeting Summary\n- Add/modify items as needed"
    summary["editable_text"] = edited_text

    try:
        send_email(
            subject="Meeting Summary",
            body=summary["editable_text"],
            recipients=[os.getenv("SMTP_USER")]
        )
        share_status = f"Email sent successfully to {os.getenv('SMTP_USER')}"
    except Exception as e:
        share_status = f"Email sending failed: {e}"

    return JSONResponse({
        "info": "One-click test completed",
        "transcript_id": transcript_id,
        "summary_id": summary_id,
        "edited_text": edited_text,
        "share_status": share_status,
        "note": "To test each step individually, use /upload, /summarize, /summary, and /share endpoints separately."
    })
