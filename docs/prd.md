# High-Level PRD — POC Outreach Workflow

## 1) One-liner

Proof-of-concept app to demonstrate end-to-end outreach: define ICP → fetch companies & stakeholders from Crust Data → generate personalized emails with Claude → send via SMTP.

---

## 2) Goals

* Show a working flow from ICP selection to email send.
* Keep architecture lightweight and easy to iterate.
* Provide minimal reporting (what was sent, success/fail).

---

## 3) Scope (In / Out)

**In:**

* Industry dropdown + basic filters.
* Crust Data search (companies + people).
* Simple scoring logic (industry/revenue/headcount).
* Email draft generation via Claude.
* Send via SMTP and log results.

**Out:**

* LinkedIn automation.
* CRM integrations.
* Advanced scheduling, throttling, analytics.

---

## 4) Flow

1. User defines ICP (industry, revenue, headcount).
2. System fetches companies from Crust Data.
3. Companies scored and displayed in simple table.
4. Stakeholders pulled via People API.
5. Claude generates short outreach emails per contact.
6. Emails sent through SMTP, results logged.

---

## 5) Tech Stack (POC)

* **Frontend**: React (minimal UI for ICP → results → email preview).
* **Backend**: FastAPI (Python) to wrap Crust + Claude + SMTP.
* **DB**: SQLite (store ICP, companies, contacts, sent logs).

---

## 6) Deliverables

* Working demo with real Crust + Claude calls.
* UI to go from ICP → scored companies → people → email drafts.
* Ability to send at least one email successfully via SMTP.

---

## 7) Future Extensions

* LinkedIn draft generation.
* CRM sync.
* More sophisticated scoring and reporting.
