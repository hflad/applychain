# Notifications

This folder contains templates for notification messages sent by scheduled tasks or workflow triggers.

---

## Notification Types

- **Job digest** — New matching roles found during daily search
- **Application reminder** — Reminder to follow up on an application
- **Pipeline summary** — Weekly status of all active applications
- **Error alert** — Something in an automated workflow failed and needs attention

---

## Delivery Methods

Notifications can be delivered via:
- Claude chat (in-session messages)
- Email (if configured in `.env`)
- Slack (if webhook is configured in `.env`)

---

## Template Files

- `job_digest.md` — Template for daily job digest message
- `pipeline_summary.md` — Template for weekly pipeline report

Edit these templates to change the format or content of your notifications.
