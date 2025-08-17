import requests

BASE_URL = "http://127.0.0.1:8000"

# 1️⃣ Upload transcript
r = requests.post(f"{BASE_URL}/upload", json={"transcript_text": "This is a test meeting transcript."})
print("Upload Response:", r.json())
transcript_id = r.json()["transcript_id"]

# 2️⃣ Summarize
r = requests.post(f"{BASE_URL}/summarize", json={"transcript_id": transcript_id, "instruction": "Summarize for action items."})
print("Summarize Response:", r.json())
summary_id = r.json()["summary_id"]

# 3️⃣ Edit summary
r = requests.put(f"{BASE_URL}/summary", json={"summary_id": summary_id, "edited_text": "# Updated Summary\n- Modify items"})
print("Edit Response:", r.json())

# 4️⃣ Share via email
r = requests.post(f"{BASE_URL}/share", json={"summary_id": summary_id, "recipients": ["lou24@ethereal.email"]})
print("Share Response:", r.json())
