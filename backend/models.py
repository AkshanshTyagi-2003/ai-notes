from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# -----------------------------
# SQLAlchemy Models
# -----------------------------
class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    summaries = relationship("Summary", back_populates="transcript")


class Summary(Base):
    __tablename__ = "summaries"
    id = Column(String, primary_key=True, index=True)
    transcript_id = Column(String, ForeignKey("transcripts.id"))
    structured = Column(JSON)
    editable_text = Column(Text)
    generated_text = Column(Text)
    transcript = relationship("Transcript", back_populates="summaries")

# -----------------------------
# Pydantic Models for API
# -----------------------------
class UploadRequest(BaseModel):
    transcript_text: str

class SummarizeRequest(BaseModel):
    transcript_id: str
    instruction: str

class SaveEditRequest(BaseModel):
    summary_id: str
    edited_text: str

class ShareRequest(BaseModel):
    summary_id: str
    recipients: List[EmailStr]

class SummaryResponse(BaseModel):
    summary_id: str
    summary_text: str
    structured: Dict[str, Any] = {}
