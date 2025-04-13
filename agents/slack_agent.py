import csv
import os
from dotenv import load_dotenv
from portia import (
    Config,
    Portia,
    LLMProvider,
    LLMModel,
    LogLevel,
    execution_context,
    PlanRunState
)

# Load environment variables
load_dotenv()

# Base path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
TASKS_CSV = os.path.join(DATA_DIR, "tasks.csv")

# Setup Portia
config = Config.from_default(
    portia_api_key=os.getenv("PORTIA_API_KEY"),
    llm_provider=LLMProvider.AZURE_OPENAI,
    llm_model_name=LLMModel.AZURE_GPT_4_O,
    default_log_level=LogLevel.INFO
)

portia = Portia(config=config)

SLACK_USER_ID = "U07N0RX29JB"  # Your Slack ID


def notify_doctor(task):
    with execution_context(end_user_id="slack-agent"):
        print(f"📨 Sending Slack DM for {task['assigned_to']} regarding patient {task['patient_id']}")

        prompt = (
            f"Send a Slack message with message: 'Nurse has uploaded a task for patient {task['patient_id']} "
            f"requiring your approval: {task['details']}. Please review it in the dashboard.' "
            f"Target Slack user ID is: {SLACK_USER_ID}"
        )

        plan = portia.plan(prompt)
        run = portia.run_plan(plan)

        if run.state != PlanRunState.COMPLETE:
            print("⏳ Waiting for Slack OAuth authentication or clarification...")
            portia.wait_for_ready(run)

        print("✅ Slack message sent!")


def main():
    if not os.path.exists(TASKS_CSV):
        print(f"❌ tasks.csv not found at {TASKS_CSV}")
        return

    with open(TASKS_CSV, "r") as f:
        reader = csv.DictReader(f)
        tasks = list(reader)

    for task in tasks:
        if task["task_type"] == "book_specialist" and task["status"] == "pending":
            notify_doctor(task)


if __name__ == "__main__":
    main()
