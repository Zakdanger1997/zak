# Mailing Outreach System — Setup Guide

## What This Does
- Imports contacts from Apollo / TraceParts (CSV)
- Sends initial outreach email + 3 follow-ups (day 3, 7, 14)
- Detects replies from your inbox automatically
- Notifies you instantly when someone replies
- Sends you a daily checklist of who needs a call

---

## Step 1: Set Up the Database (PostgreSQL)

1. Create a PostgreSQL database named `mailing`
2. Run `docs/database_schema.sql` to create the tables

---

## Step 2: Set Up n8n Credentials

In n8n go to **Settings → Credentials** and create:

| Credential Name | Type | Notes |
|---|---|---|
| `Mailing DB` | PostgreSQL | Point to your PostgreSQL DB |
| `Gmail Outreach` | Gmail OAuth2 | The email you're sending FROM |

---

## Step 3: Set n8n Variables

In **Settings → Variables**, create:

| Variable | Example Value | Description |
|---|---|---|
| `SENDER_EMAIL` | you@yourdomain.com | Your outreach email |
| `NOTIFY_EMAIL` | you@personal.com | Where you get alerts |
| `DASHBOARD_URL` | http://your-n8n/dashboard | Optional dashboard link |

---

## Step 4: Import the Workflows

In n8n go to **Workflows → Import** and import these files in order:

1. `workflows/01_import_contacts.json` — Import contacts from CSV
2. `workflows/02_send_and_followup.json` — Email sending + follow-up loop
3. `workflows/03_reply_detection.json` — Detect replies + notify you
4. `workflows/04_daily_checklist.json` — Morning checklist report

---

## Step 5: Activate Workflows

Activate workflows 2, 3, and 4 (they run on schedule/trigger).
Workflow 1 is manual — run it whenever you import a new contact list.

---

## Step 6: Import Contacts

1. Export contacts from Apollo or TraceParts as CSV
2. In n8n, open **Workflow 01 - Import Contacts**
3. In the "Read CSV File" node, upload your CSV
4. Click **Execute Workflow**

### Supported CSV Columns (auto-detected)
- First Name / first_name / FirstName
- Last Name / last_name / LastName
- Email / email / Email Address
- Company / company / Account Name
- Title / title / Job Title
- Phone / phone / Mobile Phone

---

## Email Follow-up Schedule

| Email | When |
|---|---|
| Initial | Immediately when imported |
| Follow-up 1 | 3 days after initial (no reply) |
| Follow-up 2 | 7 days after initial (no reply) |
| Follow-up 3 | 14 days after initial (no reply) |
| Marked "No Response / Needs Call" | 21+ days, 4 follow-ups done |

---

## Contact Status Flow

```
new → emailed → replied         ← you get notified, needs_call = true
             → no_response      ← 21 days no reply, needs_call = true
```

## Daily Report (8 AM Mon-Fri)

You receive an email with:
- Overall stats by status
- **Call checklist** — everyone who replied or hit max follow-ups
- Pending contacts still awaiting reply
