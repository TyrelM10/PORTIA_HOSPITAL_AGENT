import csv
from datetime import datetime
from pathlib import Path

TASKS_FILE = Path("../data/tasks.csv")

def load_tasks():
    with open(TASKS_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

def save_tasks(tasks, fieldnames):
    with open(TASKS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tasks)

def prompt_doctor(task):
    print(f"\n📝 Review Task ID: {task['task_id']}")
    print(f"Patient ID: {task['patient_id']}")
    print(f"Details: {task['details']}")
    choice = input("Approve this task? (y/n): ").strip().lower()
    if choice == "y":
        return "approved", ""
    else:
        reason = input("Enter rejection reason: ").strip()
        return "rejected", reason

def main():
    tasks, fieldnames = load_tasks()

    # Add rejection_reason field if not present
    if "rejection_reason" not in fieldnames:
        fieldnames.append("rejection_reason")
        for t in tasks:
            t["rejection_reason"] = ""

    updated = False
    for task in tasks:
        if task["task_type"] == "book_specialist" and task["status"] == "pending":
            status, reason = prompt_doctor(task)
            task["status"] = status
            task["rejection_reason"] = reason
            updated = True

    if updated:
        save_tasks(tasks, fieldnames)
        print("\n✅ Tasks updated successfully!")
    else:
        print("✅ No tasks needed approval.")

if __name__ == "__main__":
    main()
