# Phase 2 Plan: Sudan Conflict Impact Dataset

**Status**: Source collection and schema review in progress  
**Start Date**: 2026-07-13  
**Geographic Focus**: Sudan (North and South Darfur, Khartoum, El Jazira, Gedaref)  
**Conflict**: Sudanese Civil Conflict (RSF vs. SAF; inter-Arab tensions; ethnic violence)

---

## Phase 2 Overview

Phase 2 extends the CIVID dataset to capture verified incidents from Sudan's ongoing conflict, with a focus on humanitarian impact, displacement, violence patterns, and access restrictions. The phase will use the same schema and verification standards as Phase 1 but will focus on different source types and geographic contexts.

### Geographic Scope

- **North Darfur**: Ethnic tensions, RSF-SAF clashes, displacement in IDP camps
- **South Darfur**: Khartoum-adjacent violence, displacement patterns
- **Khartoum**: Urban warfare, casualties from airstrikes and shelling
- **El Jazira**: Agricultural disruption, access to markets
- **Gedaref**: Cross-border impacts, refugee movements

### Conflict Categories for Phase 2

1. **Armed Clashes**: RSF vs. SAF direct combat, casualties
2. **Indiscriminate Violence**: Airstrikes, shelling in civilian areas
3. **Displacement & Access**: IDP camps, humanitarian corridors, crossing restrictions
4. **Ethnic/Communal Violence**: Inter-Arab tensions, militia violence
5. **Health System Impact**: Hospital closures, medication shortages, disease outbreaks
6. **Food Security**: Market disruption, agricultural access, famine warnings
7. **Education Disruption**: School closures, displaced students
8. **Sexual Violence**: Gender-based violence in conflict zones

---

## Verified Sources for Phase 2

### Priority 1 (High Reliability - IOs/NGOs with ground presence)

| Source ID | Organization | Type | URL | Coverage |
|-----------|--------------|------|-----|----------|
| `ocha_sudan_sitrep` | UN OCHA Sudan | Situation Reports | https://www.unocha.org/sudan | Humanitarian snapshot, access, displacement |
| `unocha_humanitarian` | UN OCHA Humanitarian Response | Response Coordin. | https://response.reliefweb.int/ | Aggregated humanitarian incidents |
| `unhcr_sudan` | UNHCR Sudan | Refugee Agency | https://www.unhcr.org/sudan | Displacement, refugee movements |
| `who_sudan_health` | WHO Sudan | Health Agency | https://www.emro.who.int/sudan/ | Health system, disease surveillance |
| `icrc_sudan` | International Committee of the Red Cross | Conflict Monitor | https://www.icrc.org/en/where-we-work/africa/sudan | Casualty figures, detention conditions |

### Priority 2 (Medium Reliability - NGO monitoring)

| Source ID | Organization | Type | URL | Coverage |
|-----------|--------------|------|-----|----------|
| `hrw_sudan` | Human Rights Watch | Rights Monitoring | https://www.hrw.org/africa/sudan | Violence documentation, civilian impact |
| `amnesty_sudan` | Amnesty International | Rights Org | https://www.amnesty.org/en/countries/africa/sudan/ | Allegations, documentation |
| `acled_sudan` | ACLED Conflict Data | Event Database | https://acleddata.com/ | Structured conflict event data |

### Priority 3 (Corroborating sources - media/academic)

| Source ID | Organization | Type | URL | Coverage |
|-----------|--------------|------|-----|----------|
| `reliefweb_sudan` | ReliefWeb | Aggregator | https://reliefweb.int/country/sdn | News, reports aggregation |
| `crisis_evidence` | Crisis Evidence Lab | Research | https://www.disasterevo.org/ | Crisis analysis, patterns |

---

## Schema Confirmation for Phase 2

**The CIVID schema (civid_schema.json) applies unchanged to Phase 2.**

Key fields:
- **record_id**: Unique identifier (phase2_sudan_*) 
- **event_id**: Incident identifier (EVT-### numbering continues from Phase 1)
- **phase**: phase2_sudan
- **country**: Sudan
- **conflict_name**: Sudanese Civil Conflict / RSF-SAF Conflict
- **verification_status**: verified | estimated | unverified | disputed
- **confidence_level**: high | medium | low
- **location_type**: city | area | health_facility | camp | school | infrastructure | etc.

All Phase 2 records must include:
- Source citation with URL
- Verification status and confidence rating
- Geographic coordinates or named location
- Date or date range
- Impact category (casualties, displacement, health, access, etc.)

---

## Data Collection Workflow for Phase 2

### Step 1: Source Review (Current)
- ✅ Compile trusted source list
- ✅ Confirm schema applicability
- ⏳ Awaiting user review and approval

### Step 2: Source Material Extraction (Pending)
- [ ] Fetch latest situation reports from OCHA Sudan
- [ ] Extract casualty figures from ICRC/WHO
- [ ] Collect displacement and camp status from UNHCR
- [ ] Review health system reports
- [ ] Document ethnic violence and militia activities
- [ ] Track market access and food security incidents

### Step 3: Record Entry & Citation
- [ ] Create structured event rows with source attribution
- [ ] Populate person records where source supports individual data
- [ ] Assign verification confidence scores
- [ ] Link to source metadata

### Step 4: Quality Assurance
- [ ] Cross-check figures across sources
- [ ] Flag unverifiable claims
- [ ] Validate geographic accuracy
- [ ] Confirm schema compliance

### Step 5: Publication
- [ ] Commit to Git
- [ ] Push to GitHub
- [ ] Document in phase2_analysis.ipynb

---

## Notes on Sudan Conflict Context

Sudan's conflict (2023-present) involves:
- **Primary Belligerents**: Sudanese Armed Forces (SAF) vs. Rapid Support Forces (RSF)
- **Secondary Factors**: Inter-Arab tensions, ethnic militias, humanitarian access restrictions
- **Key Displaced Areas**: Khartoum, North Darfur, South Darfur, El Jazira
- **Humanitarian Crisis**: ~3 million internally displaced, famine warnings, cholera outbreaks

Sources report varying casualty figures; **all Phase 2 entries will cite the source and note confidence level** rather than conflating estimates.

---

## Status

**Ready for**: User review of source list and schema confirmation  
**Next Action**: Once approved, proceed to source material extraction and record entry
