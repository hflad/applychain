# Scheduler

This folder contains configuration files for scheduled automation tasks.

---

## What Can Be Scheduled

- **Daily job digest** — Search LinkedIn or other job boards each morning and summarize new postings matching your preferences
- **Weekly application summary** — Report on applications submitted, status changes, and pipeline health
- **Follow-up reminders** — Alert when applications haven't had a status update in N days

---

## How to Schedule (Claude Cowork)

In Claude Desktop (Cowork mode), you can schedule tasks using natural language:

> "Every morning at 8am, search LinkedIn for new [Data Analyst] jobs matching my preferences and summarize them"

Claude will create a scheduled task that runs automatically. See `docs/scheduling_guide.md` for setup details.

---

## Example Task Configs

See the example files in this folder:
- `daily_job_digest.example.json` — template for daily job search
- `weekly_summary.example.json` — template for weekly pipeline report

---

## Notes

- Scheduled tasks should never submit applications automatically — discovery and summarization only
- Any action requiring file creation or application submission needs human approval
