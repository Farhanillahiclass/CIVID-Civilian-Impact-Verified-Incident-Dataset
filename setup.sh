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
