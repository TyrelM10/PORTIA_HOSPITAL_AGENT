import os
import csv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# Paths
TASKS_CSV = "data/tasks.csv"
DOCTORS_CSV = "data/doctors.csv"
PATIENTS_CSV = "data/patients.csv"

# Email config
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

    updated = False

    for task in tasks:
        if task["status"] == "done" and task["task_type"] == "book_specialist":
            patient_id = task["patient_id"]
            patient_email = patients.get(patient_id)
            doctor_email = doctors.get(task["assigned_to"])
            details = task["details"]

            # Create simulated appointment time
            start_time = datetime.now() + timedelta(days=1)
            formatted_time = start_time.strftime("%Y-%m-%d at %I:%M %p")

            if patient_email:
                send_email(
                    patient_email,
                    subject="📅 Appointment Approved",
                    body=f"Your appointment with specialist {task['assigned_to']} has been confirmed.\n\nDetails: {details}\nScheduled for: {formatted_time}"
                )

            if doctor_email:
                send_email(
                    doctor_email,
                    subject="👨‍⚕️ Appointment Scheduled",
                    body=f"An appointment has been scheduled with patient ID: {patient_id}.\n\nDetails: {details}\nTime: {formatted_time}"
                )

            task["status"] = "calendar_sent"
            updated = True

    if updated:
        with open(TASKS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=tasks[0].keys())
            writer.writeheader()
            writer.writerows(tasks)
        print("✅ Updated task statuses to 'calendar_sent'")


if __name__ == "__main__":
    main()
