import os
import csv
import sys
from dotenv import load_dotenv
from ipfs_uploader import upload_to_ipfs  # Handles encryption + upload

# Load environment variables
load_dotenv()

# CLI usage check
if len(sys.argv) < 4:
    print("❌ Usage: python task_generator_agent.py <transcript_path> <patient_id> <nurse_id>")
    sys.exit(1)

TRANSCRIPT_PATH = sys.argv[1]
PATIENT_ID = sys.argv[2]
NURSE_ID = sys.argv[3]

BASE_DIR = os.path.dirname(__file__)
TASKS_CSV = os.path.abspath(os.path.join(BASE_DIR, "../data/tasks.csv"))

# Consistent fieldnames order
FIELDNAMES = [
    "task_id",
    "patient_id",
    "task_type",
    "details",
    "status",
    "assigned_to",
    "created_by",
    "transcript_link",
    "decryption_key"
]

def extract_event_from_transcript(transcript_text):
    text = transcript_text.lower()
    if any(word in text for word in ["prescribe", "prescribing", "medicine", "tablet", "pharmacy"]):
        return {
            "task_type": "prescribe_medicine",
            "details": "Azithromycin 250mg once daily for 3 days, Vitamin C daily for a week",
            "assigned_to": "pharmacist"
        }
    elif any(word in text for word in ["appointment", "specialist", "refer", "consult", "orthopedic"]):
        return {
            "task_type": "book_specialist",
            "details": "Orthopedic, persistent back pain",
            "assigned_to": "dr_ortho"
        }
    return None

def main():
    print(f"\n📍 Transcript Path: {TRANSCRIPT_PATH}")
    print(f"🆔 Patient ID: {PATIENT_ID}, Nurse ID: {NURSE_ID}")

    if not os.path.exists(TRANSCRIPT_PATH):
        print("❌ Transcript file not found.")
        return

    with open(TRANSCRIPT_PATH, "r") as f:
        transcript = f.read()

    print(f"\n📜 Transcript:\n{transcript}\n")

    task = extract_event_from_transcript(transcript)
    if task is None:
        print("⚠️ No actionable task found.")
        return

    # Generate task ID
    task_id = "T001"
    tasks = []
    if os.path.exists(TASKS_CSV):
        with open(TASKS_CSV, "r", newline="") as f:
            reader = csv.DictReader(f)
            tasks = list(reader)
            if tasks:
                last_id = int(tasks[-1]["task_id"].replace("T", ""))
                task_id = f"T{last_id + 1:03}"

    # 🔐 Encrypt and upload transcript
    ipfs_link, decryption_key = upload_to_ipfs(TRANSCRIPT_PATH)
    print(f"🔗 Uploaded to IPFS: {ipfs_link}")

    # ✅ Prepare new task row
    new_row = {
        "task_id": task_id,
        "patient_id": PATIENT_ID,
        "task_type": task["task_type"],
        "details": task["details"],
        "status": "pending" if task["task_type"] == "book_specialist" else "done",
        "assigned_to": task["assigned_to"],
        "created_by": NURSE_ID,
        "transcript_link": ipfs_link or "",
        "decryption_key": decryption_key or ""
    }

    file_exists = os.path.exists(TASKS_CSV)
    write_header = not file_exists or os.stat(TASKS_CSV).st_size == 0

    with open(TASKS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(new_row)

    print(f"✅ Task added to {TASKS_CSV}:\n{new_row}")

if __name__ == "__main__":
    main()
