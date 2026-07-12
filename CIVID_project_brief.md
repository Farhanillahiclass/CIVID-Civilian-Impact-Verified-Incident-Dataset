# CIVID — Verified Conflict Impact Dataset (All-in-One Project Brief)

> Give this entire file to GitHub Copilot Chat (Agent mode) in VS Code and say:
> **"Set up this project following the instructions in this file."**
> Copilot should create the repo structure, the setup.sh, environment.yml, and schema file exactly as specified below, then run setup.sh.

---

## 1. Auto-Setup / Bootstrap (Copilot: do this first)

If the repo is empty or freshly opened:
1. Create the folder structure listed in Section 5.
2. Create `setup.sh` with the exact content from Section 6.
3. Create `environment.yml` with the exact content from Section 7.
4. Create `schema/civid_schema.json` with the exact content from Section 8.
5. Run `bash setup.sh` in the terminal (agent/terminal mode).
6. Confirm the `civid` conda environment was created and activate it (`conda activate civid`).
7. Confirm current phase (default: **Phase 1 — Palestine/Gaza**) before starting any extraction work.

Do not re-run `git init` or recreate the conda env if they already exist — check first (`conda env list`, `git status`) and only create what's missing.

---

## 2. Role

Act as an expert conflict-data research assistant, data engineer, metadata specialist, and ML dataset architect, helping build a clean, verified, multi-country conflict impact dataset for research and machine learning.

## 3. Core Principle

Use **verified information only**.
- Do not invent facts. Do not guess missing values.
- Do not infer sensitive attributes unless explicitly stated in a source.
- If a claim is uncertain, mark it `unknown` or `unverified`.
- If data cannot be verified from a reliable source, exclude it or flag it clearly.

## 4. Legal & Ethical Rules

- Preserve source citations for every record; track provenance for every field where possible.
- Never present unverified or speculative information as fact.
- Do not violate privacy, safety, or copyright rules.
- Do not include private images, doxxing material, or unsafe victim photos.
- Handle media involving minors, victims, and casualties cautiously and ethically.
- Only use publicly accessible, permitted, or clearly reusable images — always with source and license notes.
- Keep dataset licensing and code licensing separate from source-data licensing.
- Final dataset must be usable for research, analytics, and ML **without misleading claims**.

### Project Scope — Phased Build
Work one country/conflict area at a time. Do not mix countries within a phase unless explicitly instructed.

| Phase | Scope |
|---|---|
| 1 | Palestine / Gaza |
| 2 | Sudan |
| 3 | Iran-related conflict events — only if scope is clearly defined and reliable sources exist |
| 4 | Additional countries — only after earlier phases are complete |

### Approved Sources
UN OCHA, UNRWA, OHCHR, ACLED, UN reports on children and armed conflict, official government/humanitarian reports, Reuters/AP/BBC (corroboration only), court/sanctions/investigative documents.
**Never use:** blogs, opinion pieces, copied Wikipedia text, scraped social media, uncited claims.

### Dataset Tables
`events`, `persons`, `sources`, `media`, `entities`, `roles` — kept separate and linkable.

### Age & Role Rules
- Under 18 = `child`. 18+ = `adult`. If age unavailable, use `age_group` or `unknown` — never fabricate.
- If a role isn't directly supported by the source, mark `unverified`.

### Role Taxonomy (controlled vocabulary)
`child`, `adult civilian`, `doctor`, `nurse`, `medic / paramedic`, `teacher`, `journalist`, `student`, `aid worker`, `political leader`, `military commander`, `local commander`, `fighter / combatant`, `unknown`

### Citation & Provenance Rules
- Every row needs at least one citation (`source_url` + `citation_text`).
- Multiple supporting sources → store all of them.
- Disagreeing sources → log in `notes`, adjust `verification_status`.
- Never blend verified facts with assumptions in the same field.

### Image Handling
Only publicly accessible, ethically usable images, with URL/source/license. If unsafe/unavailable, leave blank. No identifiable images of children unless already public, relevant, and ethically safe for research.

### Data Quality Requirements
Deduplication, normalization, source reliability scoring, missing-data/ambiguity flags, entity resolution, role hierarchy mapping, timeline ordering, phase separation, human-review queue for low-confidence rows, export-ready CSV/JSON, README + data dictionary, license/usage disclaimer.

### Workflow Per Phase
1. Define phase scope → 2. Collect source candidates → 3. Extract structured records → 4. Normalize/clean → 5. Deduplicate, assign confidence → 6. Build citation/provenance links → 7. Produce CSV + JSON → 8. Write data dictionary → 9. Recommend next phase.

### Required Output Order (every phase deliverable)
1. Phase summary 2. Source list 3. Data schema 4. Citation/provenance plan 5. Extracted records table 6. Data quality notes 7. Missing fields policy 8. Licensing/safety notes 9. Next actions

### Hard Rules
- Never output anything not supported by sources.
- Never mix countries in one phase unless asked.
- Aggregate-only source data → label as aggregate, don't force into person-level rows.
- Keep verified/estimated/unverified clearly distinct.
- Prefer structured tables over prose; prefer CSV/JSON compatibility.
- **Traceability over completeness** when the two conflict.

---

## 5. Folder Structure (Copilot: create this)

```
civid-dataset/
├── .github/
│   └── copilot-instructions.md   (copy of this file)
├── data/
│   ├── phase1_palestine/
│   │   ├── events.csv
│   │   ├── persons.csv
│   │   └── sources.csv
│   └── phase2_sudan/
├── schema/
│   └── civid_schema.json
├── src/
├── notebooks/
├── setup.sh
├── environment.yml
└── README.md
```

---

## 6. setup.sh (Copilot: create this file with exact content, then run it)

```bash
#!/usr/bin/env bash
set -e

echo "== CIVID Dataset — Bootstrap Setup =="

# 1. Folder structure
mkdir -p .github data/phase1_palestine data/phase2_sudan schema src notebooks
echo "[ok] Folder structure ready"

# 2. Git init (only if not already a repo)
if [ ! -d ".git" ]; then
  git init
  echo "[ok] Git initialized"
else
  echo "[skip] Git already initialized"
fi

# 3. Conda environment (only if it doesn't already exist)
if conda env list | grep -q "^civid "; then
  echo "[skip] Conda env 'civid' already exists"
else
  conda env create -f environment.yml
  echo "[ok] Conda env 'civid' created"
fi

# 4. Starter CSVs with headers (Phase 1 default)
EVENTS_CSV="data/phase1_palestine/events.csv"
PERSONS_CSV="data/phase1_palestine/persons.csv"
SOURCES_CSV="data/phase1_palestine/sources.csv"

if [ ! -f "$EVENTS_CSV" ]; then
  echo "record_id,phase,country,conflict_name,event_id,event_date,location,location_type,source_id,fatalities,injuries,missing,verification_status,confidence_level,notes" > "$EVENTS_CSV"
fi

if [ ! -f "$PERSONS_CSV" ]; then
  echo "record_id,event_id,victim_name,victim_alias,victim_age,victim_age_group,victim_gender,victim_role,occupation,doctor_flag,nurse_flag,medic_flag,teacher_flag,journalist_flag,student_flag,child_flag,adult_flag,civilian_flag,combatant_flag,leader_flag,commander_flag,organization_affiliation,image_available,image_url,image_source,image_license,image_caption,media_warning,verification_status,notes" > "$PERSONS_CSV"
fi

if [ ! -f "$SOURCES_CSV" ]; then
  echo "source_id,source_name,source_url,source_type,source_date,citation_text,reliability_score" > "$SOURCES_CSV"
fi
echo "[ok] Starter CSVs ready"

if [ ! -f "schema/civid_schema.json" ]; then
  echo "[warn] schema/civid_schema.json not found — create it from Section 8 of the project brief"
fi

echo ""
echo "== Done. Next steps: =="
echo "1. conda activate civid"
echo "2. Open Copilot Chat and say: 'Start Phase 1 source collection'"
```

---

## 7. environment.yml (Copilot: create this file with exact content)

```yaml
name: civid
channels:
  - conda-forge
dependencies:
  - python=3.11
  - pandas
  - pip
  - pip:
      - jsonschema
      - pydantic
      - requests
      - beautifulsoup4
```

---

## 8. schema/civid_schema.json (Copilot: create this file with exact content)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CIVID Conflict Impact Record",
  "type": "object",
  "properties": {
    "record_id": { "type": "string" },
    "phase": { "type": "string" },
    "country": { "type": "string" },
    "conflict_name": { "type": "string" },
    "event_id": { "type": "string" },
    "event_date": { "type": "string", "format": "date" },
    "location": { "type": "string" },
    "location_type": { "type": "string" },
    "source_id": { "type": "string" },
    "source_name": { "type": "string" },
    "source_url": { "type": "string", "format": "uri" },
    "source_type": { "type": "string" },
    "source_date": { "type": "string", "format": "date" },
    "citation_text": { "type": "string" },
    "verification_status": {
      "type": "string",
      "enum": ["verified", "estimated", "unverified", "disputed"]
    },
    "confidence_level": {
      "type": "string",
      "enum": ["high", "medium", "low"]
    },
    "victim_name": { "type": ["string", "null"] },
    "victim_alias": { "type": ["string", "null"] },
    "victim_age": { "type": ["integer", "null"] },
    "victim_age_group": { "type": ["string", "null"] },
    "victim_gender": { "type": ["string", "null"] },
    "victim_role": {
      "type": "string",
      "enum": [
        "child", "adult civilian", "doctor", "nurse", "medic / paramedic",
        "teacher", "journalist", "student", "aid worker",
        "political leader", "military commander", "local commander",
        "fighter / combatant", "unknown"
      ]
    },
    "occupation": { "type": ["string", "null"] },
    "doctor_flag": { "type": "boolean" },
    "nurse_flag": { "type": "boolean" },
    "medic_flag": { "type": "boolean" },
    "teacher_flag": { "type": "boolean" },
    "journalist_flag": { "type": "boolean" },
    "student_flag": { "type": "boolean" },
    "child_flag": { "type": "boolean" },
    "adult_flag": { "type": "boolean" },
    "civilian_flag": { "type": "boolean" },
    "combatant_flag": { "type": "boolean" },
    "leader_flag": { "type": "boolean" },
    "commander_flag": { "type": "boolean" },
    "organization_affiliation": { "type": ["string", "null"] },
    "fatalities": { "type": ["integer", "null"], "minimum": 0 },
    "injuries": { "type": ["integer", "null"], "minimum": 0 },
    "missing": { "type": ["integer", "null"], "minimum": 0 },
    "image_available": { "type": "boolean" },
    "image_url": { "type": ["string", "null"], "format": "uri" },
    "image_source": { "type": ["string", "null"] },
    "image_license": { "type": ["string", "null"] },
    "image_caption": { "type": ["string", "null"] },
    "media_warning": { "type": ["string", "null"] },
    "notes": { "type": ["string", "null"] }
  },
  "required": [
    "record_id", "phase", "country", "event_date",
    "source_id", "source_url", "citation_text",
    "verification_status", "confidence_level"
  ],
  "additionalProperties": false
}
```

---

## 9. Start Command

Once setup is done, begin Phase 1 by producing (in this exact order): source list → data schema confirmation → citation/provenance plan → first extraction plan for Palestine/Gaza. Do not proceed to Phase 2 until Phase 1 deliverables are complete and reviewed.
