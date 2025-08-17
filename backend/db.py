from typing import Dict
from uuid import uuid4
store: Dict[str, dict] = {}

def db_init():
    pass

def create_summary(transcript_text: str) -> str:
    sid = str(uuid4())
    store[sid] = {"id": sid, "transcript_text": transcript_text, "generated_text": "", "edited_text": ""}
    return sid

def get_summary_by_id(sid: str):
    return store.get(sid)

def update_summary_text(sid: str, edited: str):
    rec = store.get(sid)
    if not rec: return False
    rec["edited_text"] = edited
    return True

def log_email(sid: str, recipients):
    rec = store.get(sid)
    if rec:
        rec.setdefault("emails", []).append({"to": recipients})
