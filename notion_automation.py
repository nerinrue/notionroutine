import os
from datetime import datetime, timedelta
from notion_client import Client

NOTION_TOKEN = "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"
DAILY_DB_ID = "22a37ea6680f80d3bfccd5c1e86a5d58"
WEEKLY_DB_ID = "22c37ea6680f807faf8ee351a1845823"

notion = Client(auth=NOTION_TOKEN)

# Example daily tasks
DAILY_TASKS = ["Exercise", "Read", "Meditate", "Plan day"]

def add_daily_tasks(date):
    for task in DAILY_TASKS:
        notion.pages.create(
            parent={"database_id": DAILY_DB_ID},
            properties={
                "Task": {"title": [{"text": {"content": task}}]},
                "Date": {"date": {"start": date}},
                "Status": {"select": {"name": "To Do"}},
            }
        )

def update_progress_rate(date):
    # Query all tasks for the date
    results = notion.databases.query(
        database_id=DAILY_DB_ID,
        filter={
            "and": [
                {"property": "Date", "date": {"equals": date}}
            ]
        }
    )["results"]
    if not results:
        return
    total = len(results)
    done = sum(1 for r in results if r["properties"]["Status"]["select"]["name"] == "Done")
    progress = round((done / total) * 100) if total else 0
    # Update each page with progress rate
    for r in results:
        notion.pages.update(
            page_id=r["id"],
            properties={"Progress Rate": {"number": progress}}
        )

def weekly_review(start_date, end_date):
    # Query all tasks in the week
    results = notion.databases.query(
        database_id=DAILY_DB_ID,
        filter={
            "and": [
                {"property": "Date", "date": {"on_or_after": start_date}},
                {"property": "Date", "date": {"on_or_before": end_date}}
            ]
        }
    )["results"]
    total = len(results)
    done = sum(1 for r in results if r["properties"]["Status"]["select"]["name"] == "Done")
    progress = round((done / total) * 100) if total else 0
    notion.pages.create(
        parent={"database_id": WEEKLY_DB_ID},
        properties={
            "Week": {"title": [{"text": {"content": f"{start_date} - {end_date}"}}]},
            "Completed Tasks": {"number": done},
            "Progress Rate": {"number": progress},
            "Notes": {"rich_text": [{"text": {"content": "Auto-generated review."}}]}
        }
    )

if __name__ == "__main__":
    today = datetime.now().date().isoformat()
    add_daily_tasks(today)
    update_progress_rate(today)
    # For weekly review, run this on Sundays (or your preferred day)
    if datetime.now().weekday() == 6:  # Sunday
        start = (datetime.now() - timedelta(days=6)).date().isoformat()
        end = today
        weekly_review(start, end)
