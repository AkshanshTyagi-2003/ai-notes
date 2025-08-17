import os
import json
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv
from chunking import smart_chunks
from prompts import SYSTEM_PROMPT, FUSE_PROMPT
from groq import Groq  # Correct import

# Load environment variables from .env
load_dotenv()

# Initialize Groq client with API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")


def call_groq(messages: List[Dict[str, str]]) -> str:
    """
    Call Groq chat API with a list of messages and return the content of the first choice.
    """
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2
    )
    return resp.choices[0].message.content


def generate_summary(transcript: str, instruction: str) -> Tuple[Dict[str, Any], str]:
    """
    Generate a structured summary and an editable prose version of a transcript.

    Steps:
    1. Split transcript into smart chunks.
    2. Generate partial summaries for each chunk.
    3. Fuse partial summaries into a single structured JSON and editable text.

    Returns:
        structured: dict with sections like agenda, decisions, action_items, etc.
        editable_text: str, full editable prose version.
    """
    chunks = smart_chunks(transcript)
    partials = []

    # Generate partial summaries for each chunk
    for i, ch in enumerate(chunks):
        partial = call_groq([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Custom instruction:\n{instruction}\n\nTranscript part {i+1} of {len(chunks)}:\n{ch}"}
        ])
        partials.append(partial)

    # Fuse partial summaries into structured JSON + editable text
    fused_output = call_groq([
        {"role": "system", "content": FUSE_PROMPT},
        {"role": "user", "content": f"Custom instruction:\n{instruction}\n\nCombine partial summaries into structured JSON with sections: agenda, decisions, action_items, owners, deadlines, risks, open_questions and also produce a clean editable prose version.\n\nPartials:\n" + "\n\n".join(partials)}
    ])

    # Light validation with fallback
    try:
        data = json.loads(fused_output)
        structured = data.get("structured", {"sections": [], "action_items": []})
        editable_text = data.get("editable_text", fused_output)
    except Exception:
        structured = {"sections": [], "action_items": []}
        editable_text = fused_output

    return structured, editable_text
