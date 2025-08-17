# backend/app.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
import os

from models import UploadRequest, SummarizeRequest, SaveEditRequest, ShareRequest, SummaryResponse
from llm import generate_summary
from emailer import send_email

# -----------------------------
# Database setup (in-memory SQLite for Vercel)
# -----------------------------
Base = declarative_base()

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(String, primary_key=True, index=True)
    text = Column(String)

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(String, primary_key=True, index=True)
    transcript_id = Column(String)
    structured = Column(String)
    editable_text = Column(String)
    generated_text = Column(String)

DATABASE_URL = "sqlite:///:memory:"  # temporary in-memory DB for serverless
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="AI Meeting Summarizer", description="""
**Instructions for single actions**:

1. **Upload Transcript**: Paste your transcript and click 'Try it out'. Copy the `transcript_id` from the response.
2. **Summarize Transcript**: Paste the copied `transcript_id` in the input. Add any instruction (e.g., 'Summarize in bullet points') and click 'Try it out'. Copy the `summary_id` from the response.
3. **Save/Edit Summary**: Paste the copied `summary_id` and edited text. Click 'Try it out' to save changes.
4. **Share Summary**: Paste the copied `summary_id` and recipient emails. Click 'Try it out' to send email.
""")

# -----------------------------
# Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Authentication
# -----------------------------
PREDEFINED_USERNAME = "akshanshtyagi"
PREDEFINED_PASSWORD = "password123"

def verify_auth(
    x_username: str = Header(default=PREDEFINED_USERNAME),
    x_password: str = Header(default=PREDEFINED_PASSWORD)
):
    if x_username != PREDEFINED_USERNAME or x_password != PREDEFINED_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return True

# -----------------------------
# Endpoints
# -----------------------------
@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/upload", summary="Upload Transcript")
def upload(req: UploadRequest, db: Session = Depends(get_db), auth: bool = Depends(verify_auth)):
    transcript_id = str(uuid.uuid4())
    transcript = Transcript(id=transcript_id, text=req.transcript_text)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return {"transcript_id": transcript_id, "note": "Copy this transcript_id for single summarize."}

@app.post("/summarize", response_model=SummaryResponse, summary="Summarize Transcript")
def summarize(req: SummarizeRequest, db: Session = Depends(get_db), auth: bool = Depends(verify_auth)):
    transcript = db.query(Transcript).filter(Transcript.id == req.transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    structured, editable_text = generate_summary(transcript.text, req.instruction)

    summary_id = str(uuid.uuid4())
    summary = Summary(
        id=summary_id,
        transcript_id=transcript.id,
        structured=structured,
        editable_text=editable_text,
        generated_text=editable_text
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)

    return SummaryResponse(
        summary_id=summary.id,
        summary_text=summary.editable_text,
        structured=structured
    )

@app.put("/summary", summary="Save/Edit Summary")
def save_edit(req: SaveEditRequest, db: Session = Depends(get_db), auth: bool = Depends(verify_auth)):
    summary = db.query(Summary).filter(Summary.id == req.summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    summary.editable_text = req.edited_text
    db.commit()
    return {"ok": True}

@app.post("/share", summary="Share Summary")
def share(req: ShareRequest, db: Session = Depends(get_db), auth: bool = Depends(verify_auth)):
    summary = db.query(Summary).filter(Summary.id == req.summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    try:
        send_email(
            subject="Meeting Summary",
            body=summary.editable_text,
            recipients=req.recipients
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {e}")

    return {"ok": True, "message": f"Email sent successfully to {', '.join(req.recipients)}"}

@app.post("/test-all", summary="One-Click Test")
def test_all(db: Session = Depends(get_db), auth: bool = Depends(verify_auth)):
    sample_text = "This is a sample meeting transcript. Discuss project deadlines and assign tasks."
    transcript_id = str(uuid.uuid4())
    transcript = Transcript(id=transcript_id, text=sample_text)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    structured, editable_text = generate_summary(
        transcript.text, "Summarize the meeting into clear sections with action items."
    )
    summary_id = str(uuid.uuid4())
    summary = Summary(
        id=summary_id,
        transcript_id=transcript_id,
        structured=structured,
        editable_text=editable_text,
        generated_text=editable_text
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)

    edited_text = "# Updated Meeting Summary\n- Add/modify items as needed"
    summary.editable_text = edited_text
    db.commit()

    try:
        send_email(
            subject="Meeting Summary",
            body=summary.editable_text,
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
