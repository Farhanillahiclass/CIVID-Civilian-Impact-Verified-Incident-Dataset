# CIVID — Daily Auto-Update Setup

This sets up `scripts/daily_update.py` to run automatically once a day. It fetches
new candidate humanitarian reports from the **official ReliefWeb API** (public, no
key required) and drops them into `data/staging/pending_review.csv`.

## Important: this does NOT auto-add data to your verified dataset

New reports go into a **staging file**, marked `verification_status = unverified`
and `confidence_level = low`. You must manually review each one, write a proper
`citation_text`, decide the correct `victim_role` / fields, and copy it into the
real `events.csv` yourself — exactly like the manual process you've been using.
This preserves the traceability and no-fabrication rules from the project's core
instructions. A dataset that auto-merges unverified scraped data would break the
whole point of the project.

## One-time setup

### Step 0: Register your appname (required since Nov 2025)
ReliefWeb now requires a **pre-approved appname** before the API will respond
with real data (unapproved requests get odd status codes like 202/400/empty
responses instead of a clean error — this is expected, not a bug in the script).

1. Go to **https://apidoc.reliefweb.int/** and look for the appname request
   form/link near the top of the page (worded as "Request an appname").
2. Fill it in with: your name/organization, the purpose ("non-commercial
   humanitarian research dataset — CIVID"), and a proposed appname such as
   `civid-research-<yourname>`.
3. Submit and wait for ReliefWeb's approval email — timing isn't guaranteed.
4. Once approved, update `APPNAME` in `scripts/daily_update.py` to match
   **exactly** the approved string.
5. Until approval comes through, the script will print a clear warning and
   simply find no new reports — it won't crash or corrupt anything.

### Step 1: test manually
```bash
conda activate civid
python scripts/daily_update.py   # test it manually first
```

Check `data/staging/pending_review.csv` — you should see new rows with report
titles, dates, and source URLs waiting for your review.

## Schedule it to run daily (Windows Task Scheduler)

1. Open **Task Scheduler** (search it in the Start menu)
2. Click **Create Basic Task**
3. Name: `CIVID Daily Update`
4. Trigger: **Daily**, pick a time (e.g. 8:00 AM)
5. Action: **Start a program**
6. Program/script:
   ```
   C:\Users\Muhammad Anas\miniconda3\condabin\conda.bat
   ```
7. Add arguments:
   ```
   run -n civid python scripts/daily_update.py
   ```
8. Start in (working directory) — set this to your repo path:
   ```
   G:\CIVID (Civilian Impact Verified Incident Dataset)
   ```
9. Finish. Right-click the task → **Run** once to confirm it works, then check
   `data/staging/pending_review.csv` for new rows.

## Weekly review routine (recommended)

Once a week, open `data/staging/pending_review.csv` and for each row:
1. Open the `source_url` and actually read the report
2. If it contains a verifiable, citable fact matching the schema → copy it into
   the correct `events.csv`, fill in `citation_text` properly, set the real
   `verification_status` and `confidence_level`
3. If it's not relevant or not verifiable → delete the row from staging, or move
   it to a `data/staging/rejected.csv` for your own record-keeping
4. Commit and push as usual

## Extending to more sources later (optional)

ReliefWeb aggregates OCHA, UNHCR, WHO, and others already, so it's a good single
source to start with. If you later want to add **ACLED** directly:
- ACLED has an official API too, but requires free registration for an API key
  (https://developer.acleddata.com) — never scrape ACLED's website directly,
  always use their API with proper credentials
- The same staging pattern applies: fetch → mark unverified → human review → promote

## Why not scrape OCHA/WHO/UNHCR websites directly?

Their public sites often block automated requests (you saw this already with
Copilot's fetch attempts), and scraping HTML directly is fragile — any small site
redesign breaks it. ReliefWeb exists specifically to solve this by republishing
the same reports through a stable, documented API meant for programmatic use.
