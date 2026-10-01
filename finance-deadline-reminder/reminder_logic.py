"""
Deadline reminder logic (used inside a 'Code by Zapier' step, Python).

Input (from the previous Zapier step 'Get rows' on the Excel/Sheet knowledge base):
  rows   : list of dicts with columns
           task, deadline (YYYY-MM-DD), owner, slack_id, email, channel_pref (slack|gmail), status
  today  : 'YYYY-MM-DD' (Zapier supplies the run date)

Output: a list of messages to send + one 'all good' message if nothing is due.
Rules:
  - status 'Done' is ignored
  - deadline in 2 days -> early reminder, in 1 day -> tomorrow reminder, today -> URGENT
  - past deadline and not done -> overdue alert
  - nothing to report -> "All good, well done!"
All data in the sample file is fictional.
"""
from datetime import date, datetime


def build_messages(rows, today):
    today = datetime.strptime(today, "%Y-%m-%d").date() if isinstance(today, str) else today
    messages = []
    for r in rows:
        if str(r.get("status", "")).strip().lower() == "done":
            continue
        days = (datetime.strptime(r["deadline"], "%Y-%m-%d").date() - today).days
        if days == 2:
            tag, text = "reminder", f"Reminder: '{r['task']}' is due in 2 days ({r['deadline']})."
        elif days == 1:
            tag, text = "reminder", f"Reminder: '{r['task']}' is due TOMORROW ({r['deadline']})."
        elif days == 0:
            tag, text = "urgent", f"URGENT: '{r['task']}' is due TODAY ({r['deadline']})."
        elif days < 0:
            tag, text = "overdue", f"OVERDUE by {-days} day(s): '{r['task']}' (was due {r['deadline']})."
        else:
            continue
        pref = str(r.get("channel_pref", "slack")).strip().lower()
        messages.append({
            "type": tag,
            "channel": "gmail" if pref == "gmail" else "slack",
            "to": r["email"] if pref == "gmail" else f"<@{r['slack_id']}>",
            "owner": r["owner"],
            "text": text,
        })
    if not messages:
        messages.append({"type": "all_good", "channel": "slack", "to": "#finance-deadlines",
                         "owner": "", "text": "All good, no deadlines in the next 2 days. Well done, team!"})
    return messages


if __name__ == "__main__":
    import csv, sys
    path = sys.argv[1] if len(sys.argv) > 1 else "deadlines_sample.csv"
    run_date = sys.argv[2] if len(sys.argv) > 2 else str(date.today())
    with open(path, newline="", encoding="utf-8") as f:
        for m in build_messages(list(csv.DictReader(f)), run_date):
            print(f"[{m['type'].upper():8}] via {m['channel']:5} -> {m['to']}: {m['text']}")
