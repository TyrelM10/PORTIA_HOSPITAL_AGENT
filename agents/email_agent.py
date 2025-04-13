import csv
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# Base dir assuming this script runs from agents/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_CSV = os.path.join(BASE_DIR, "data", "tasks.csv")
DOCTORS_CSV = os.path.join(BASE_DIR, "data", "doctors.csv")
PATIENTS_CSV = os.path.join(BASE_DIR, "data", "patients.csv")
PHARMACY_CSV = os.path.join(BASE_DIR, "data", "pharmacy.csv")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        print(f"📧 Email sent to {to_email}!")


def main():
    tasks = load_csv(TASKS_CSV)
    doctors = {row["name"]: row["email"] for row in load_csv(DOCTORS_CSV)}
    patients = {row["patient_id"]: row["email"] for row in load_csv(PATIENTS_CSV)}
    pharmacy = load_csv(PHARMACY_CSV)
    pharmacy_email = pharmacy[0]["email"] if pharmacy else "daskaushik420@gmail.com"

    updated = False

    for task in tasks:
        print(f"🔍 Checking Task ID {task['task_id']} - Status: {task['status']}")

        if task["status"] != "approved" and task["task_type"] != "prescribe_medicine":
            continue

        task_type = task["task_type"]
        patient_id = task["patient_id"]
        subject = f"[Task] Patient {patient_id}"
        body = f"Task Details:\n\n{task['details']}"

        if task_type == "book_specialist" and task["status"] == "approved":
            doctor_email = doctors.get(task["assigned_to"])
            patient_email = patients.get(patient_id)

            if doctor_email:
                send_email(doctor_email, subject, f"👨‍⚕️ Doctor Notification\n\n{body}")
            if patient_email:
                send_email(patient_email, subject, f"👤 Patient Notification\n\n{body}")
            task["status"] = "done"
            updated = True

        elif task_type == "email" and task["status"] == "approved":
            patient_email = patients.get(patient_id)
            if patient_email:
                send_email(patient_email, subject, f"📄 Email Task\n\n{body}")
                task["status"] = "done"
                updated = True

        elif task_type == "prescribe_medicine" and task["status"] == "done":
            send_email(pharmacy_email, subject, f"💊 Prescription Order\n\n{body}")
            # Already marked done at generation step, no need to change
            updated = True

    if updated:
        with open(TASKS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=tasks[0].keys())
            writer.writeheader()
            writer.writerows(tasks)
        print("✅ Updated tasks marked as 'done'.")
    else:
        print("ℹ️ No tasks were updated.")


if __name__ == "__main__":
    main()
