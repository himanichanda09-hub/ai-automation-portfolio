# Finance Deadline Reminder (Zapier + Excel + Slack/Gmail + Dust)

## Problem
Finance deadlines (VAT, invoices, month-end close, expense validation) are tracked manually. Reminders are forgotten or sent late.

## Solution
A scheduled workflow reads a deadline table and sends reminders automatically, in Slack or Gmail according to each person's preference.

## Knowledge base (Excel)
See [`deadlines_sample.csv`](deadlines_sample.csv): `task, deadline, owner, slack_id, email, channel_pref, status`.

## Rules
| Situation | Action |
|---|---|
| Deadline in 2 days | Reminder |
| Deadline tomorrow | Reminder |
| Deadline today | URGENT message |
| Past deadline, not done | Overdue alert |
| Status = Done | Ignored |
| Nothing due | "All good, no deadlines in the next 2 days. Well done, team!" posted in the Finance channel |

Owner is tagged in the Slack group channel (`@name`) or receives a personal Gmail, depending on `channel_pref`.

## Workflow (Zapier)
```
Schedule (every weekday 09:00)
  -> Get rows (Excel deadline table)
  -> Code by Zapier (Python: reminder_logic.py)   # decides who gets what
  -> Paths:  Slack message (tag owner)  |  Gmail to owner  |  "All good" message
  -> (optional) Update row: last_reminder_sent
```
**Dust (optional layer):** a Dust assistant with the same sheet as knowledge lets people ask in Slack, for example "What is due this week?".

## Tested logic
`reminder_logic.py` was tested on fictional data: 2-day, 1-day, same-day, overdue, done and "all good" scenarios.
```
python reminder_logic.py deadlines_sample.csv 2026-09-30
```
Expected output:
```
[REMINDER] via slack -> <@U01ALICE>: Reminder: 'VAT declaration' is due in 2 days (2026-10-02).
[REMINDER] via gmail -> bruno@example.com: Reminder: 'Supplier invoices batch payment' is due TOMORROW (2026-10-01).
[URGENT  ] via slack -> <@U03CHLOE>: URGENT: 'Month-end close' is due TODAY (2026-09-30).
[OVERDUE ] via slack -> <@U04DAVID>: OVERDUE by 2 day(s): 'Expense reports validation' (was due 2026-09-28).
```

## Results
Fill in only what you measured or can reasonably estimate (label it): missed deadlines before/after, minutes saved per week.

## Next steps
Weekly summary to the Finance lead, escalation to a manager after 2 overdue days, acknowledgement button in Slack.
