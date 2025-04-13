# 🏥 Hospital Agent Workflow System (Powered by Portia + IPFS)

<img width="100%" alt="Dashboard Screenshot" src="https://github.com/user-attachments/assets/YOUR_DASHBOARD_SCREENSHOT_LINK_HERE">

An intelligent hospital workflow automation tool that empowers nurses and doctors to manage patient transcripts, automate administrative tasks, and securely store and share information using AI agents, IPFS, and encrypted data flows.

This system is built using **FastAPI**, **Portia AI Planning Agents**, **ChromaDB**, **Slack Integration**, and **IPFS via Pinata**, providing a seamless multi-role platform for transcript-based task automation in healthcare.

---

## 🚀 Key Features

- **Multi-role Login System**: Role-specific dashboards for nurses, doctors, and junior doctors.
- **Secure Transcript Upload**: Nurses upload patient visit transcripts, which are encrypted and stored on IPFS.
- **AI Task Extraction**: Automatically extracts and classifies tasks (email, calendar event, medication order).
- **Approval Workflow**: Doctors approve or reject tasks, with reasons logged for audit purposes.
- **Automated Execution**: Sends emails, creates calendar events, and handles prescriptions after approval.
- **Slack Notifications**: Doctors are alerted via Slack when a new task is pending.
- **IPFS Storage with Encryption**: Transcripts are securely stored on IPFS; only doctors can decrypt them.
- **Human-in-the-Loop Safety**: Critical actions require manual review for safety and compliance.

---

## 🛡️ Security & Privacy

- **Fernet Encryption**: All transcripts are encrypted before upload and decrypted only by the doctor.
- **Role-Based Access Control**: Users can only access relevant dashboard views and actions.
- **Transcript Privacy**: Decryption key is stored securely and never exposed in emails.

---

## 🗂️ How It Works

1. **Nurse uploads transcript**
   - Transcripts are encrypted using Fernet.
   - Encrypted files are uploaded to IPFS via Pinata.
   - A task is created with transcript link and key.

2. **AI Agent Extracts Tasks**
   - Using Portia + OpenAI, tasks are extracted (send prescription, schedule appointments, etc.).
   - Tasks are stored in `tasks.csv` with metadata.

3. **Slack Notification**
   - Assigned doctor receives a Slack DM about the new task.

4. **Doctor Dashboard**
   - Doctor logs in, decrypts transcript, and reviews task.
   - Can approve or reject with comments.

5. **Automated Action**
   - If approved, an email is sent or calendar event created.
   - Task status is updated in `tasks.csv`.

---

## 📸 Screenshots



- **Login Screen**  
  ![Login]<img width="1395" alt="Screenshot 2025-04-13 at 10 12 44 AM" src="https://github.com/user-attachments/assets/55c58425-b3ef-4e05-948c-2f2a6e21d519" />


- **Nurse Upload Dashboard**  
  ![Nurse](https://github.com/user-attachments/assets/NURSE_DASHBOARD_SCREENSHOT)

- **Doctor Dashboard with Decrypted Transcript**  
  ![Doctor](https://github.com/user-attachments/assets/DOCTOR_DASHBOARD_SCREENSHOT)

- **Slack Notification**  
  ![Slack](https://github.com/user-attachments/assets/SLACK_NOTIFICATION_SCREENSHOT)

- **Encrypted IPFS Transcript**  
  ![IPFS](https://github.com/user-attachments/assets/IPFS_SCREENSHOT)

---

## 🧠 Technologies Used

- **FastAPI** – Web backend
- **Portia SDK** – AI agents for task planning and automation
- **ChromaDB** – Vector search for relevant transcript chunks
- **OpenAI / Azure OpenAI** – LLM-based task classification
- **Slack API** – Doctor notification
- **Fernet (Cryptography)** – Symmetric encryption for transcripts
- **IPFS via Pinata** – Decentralized encrypted storage
- **CSV files** – Lightweight backend for MVP phase

---

## 👨‍⚕️ User Roles & Access

| Role            | Login ID         | Password   |
|-----------------|------------------|------------|
| Admin           | `nurse`          | `abcd1234` |
| Junior Doctor   | `user_id`        | `abcd1234` |
| Doctors         | From `doctors.csv` | `abcd1234` |

---

## 🔧 Setup Instructions

### Prerequisites

- Python 3.8+
- Pinata API key
- Slack bot token
- OpenAI or Azure OpenAI key
- Portia SDK installed

---

### 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/portia-hospital-agent.git
cd portia-hospital-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Fill in PINATA_API_KEY, SLACK_BOT_TOKEN, OPENAI_API_KEY, etc.

# Run the server
uvicorn main:app --reload
