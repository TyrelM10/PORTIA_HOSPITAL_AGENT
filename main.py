import os
import shutil
import subprocess
import csv
import requests
from datetime import datetime
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from cryptography.fernet import Fernet


# -------- IPFS Transcript Decryption ----------
def decrypt_ipfs_transcript(ipfs_link, decryption_key):
    try:
        response = requests.get(ipfs_link)
        response.raise_for_status()
        encrypted_data = response.content
        fernet = Fernet(decryption_key.encode())
        return fernet.decrypt(encrypted_data).decode()
    except Exception as e:
        print(f"⚠️ Error decrypting IPFS file: {e}")
        return "⚠️ Unable to decrypt transcript."

# ---------- FastAPI Setup ----------
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(TEMPLATES_DIR, "static")

TASK_CSV = os.path.join(DATA_DIR, "tasks.csv")
DOCTORS_CSV = os.path.join(DATA_DIR, "doctors.csv")

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

users = {
    "nurse": {"username": "nurse", "password": "abcd1234", "role": "nurse"},
    "user_id": {"username": "user_id", "password": "abcd1234", "role": "junior_doctor"},
}

if os.path.exists(DOCTORS_CSV):
    with open(DOCTORS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row["name"]] = {
                "username": row["name"],
                "password": row["password"],
                "role": "doctor",
                "specialisation": row["specialisation"]
            }

# ---------- Helpers ----------
def get_current_user(request: Request):
    return request.session.get("user")

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse("/login")

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user["password"] != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user"] = user
    return RedirectResponse(url=f"/{user['role']}", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/nurse", response_class=HTMLResponse)
async def nurse_dashboard(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "nurse":
        return RedirectResponse(url="/login")

    tasks = []
    if os.path.exists(TASK_CSV):
        with open(TASK_CSV, newline="") as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

    return templates.TemplateResponse("nurse.html", {
        "request": request,
        "tasks": tasks,
        "transcript_text": ""
    })

@app.post("/nurse/upload", response_class=HTMLResponse)
async def upload_transcript(
    request: Request,
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    nurse_id: str = Form(...)
):
    user = get_current_user(request)
    if not user or user["role"] != "nurse":
        return RedirectResponse(url="/login")

    filename = f"transcript_{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    filepath = os.path.join(TRANSCRIPT_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(filepath, "r") as f:
        transcript_text = f.read()

    subprocess.run(["python3", "agents/task_generator_agent.py", filepath, patient_id, nurse_id])
    subprocess.run(["python3", "agents/slack_agent.py"])
    subprocess.run(["python3", "agents/email_agent.py"])

    tasks = []
    if os.path.exists(TASK_CSV):
        with open(TASK_CSV, newline="") as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

    return templates.TemplateResponse("nurse.html", {
        "request": request,
        "msg": "Transcript uploaded successfully.",
        "tasks": tasks,
        "transcript_text": transcript_text
    })



@app.get("/doctor", response_class=HTMLResponse)
async def doctor_dashboard(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "doctor":
        return RedirectResponse(url="/login")

    pending_tasks, approved_tasks = [], []

    if os.path.exists(TASK_CSV):
        with open(TASK_CSV, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["assigned_to"].lower() == user["username"].lower():
                    if row["status"].lower() == "pending":
                        pending_tasks.append(row)
                    elif row["status"].lower().startswith("done") or row["status"].lower().startswith("calendar_sent"):
                        approved_tasks.append(row)

    # 🔓 Try to decrypt transcripts or fallback to local file
    for task in pending_tasks:
        link = task.get("transcript_link")
        key = task.get("decryption_key")

        if link and key:
            try:
                response = requests.get(link, timeout=5)
                response.raise_for_status()
                encrypted_data = response.content
                fernet = Fernet(key.encode())
                decrypted = fernet.decrypt(encrypted_data).decode()
                task["transcript_content"] = decrypted
            except Exception as e:
                print(f"⚠️ Failed to decrypt transcript from IPFS for {task['task_id']}: {e}")

                # 🔁 Fallback: read from local transcript file if exists
                local_files = os.listdir(TRANSCRIPT_DIR)
                match = [fname for fname in local_files if task["patient_id"] in fname]
                if match:
                    with open(os.path.join(TRANSCRIPT_DIR, match[-1]), "r") as f:
                        task["transcript_content"] = f.read()
                else:
                    task["transcript_content"] = "⚠️ Unable to decrypt or find local fallback."
        else:
            task["transcript_content"] = "⚠️ No transcript link or key found."

    for task in approved_tasks:
        task["transcript_content"] = None  # Don't show transcript after approval

    return templates.TemplateResponse("doctor.html", {
        "request": request,
        "pending_tasks": pending_tasks,
        "approved_tasks": approved_tasks,
        "doctor": user
    })


@app.post("/doctor/approve", response_class=RedirectResponse)
async def approve_task(
    request: Request,
    task_id: str = Form(...),
    approve: str = Form(...),
    reason: str = Form("")
):
    user = get_current_user(request)
    if not user or user["role"] != "doctor":
        return RedirectResponse(url="/login")

    updated_rows = []
    with open(TASK_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["task_id"] == task_id:
                row["status"] = "done" if approve == "y" else f"rejected: {reason or 'No reason'}"
            updated_rows.append(row)

    with open(TASK_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=updated_rows[0].keys())
        writer.writeheader()
        writer.writerows(updated_rows)

    subprocess.run(["python3", "agents/calendar_event_agent.py"])
    return RedirectResponse(url="/doctor", status_code=303)
