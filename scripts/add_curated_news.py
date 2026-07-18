#!/usr/bin/env python3
"""Append curated, source-linked real-news rows to phase news_intelligence.csv files.

Curated rows are derived from real verified events + sources already present in the
dataset (no fabricated figures). Each row cites a real source_id and source URL.
"""
import csv, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")

FIELDS = [
    "news_id", "legacy_record_id", "phase", "country", "conflict_name", "metric", "value",
    "unit", "event_or_person_scope", "news_headline", "news_summary", "news_source_url",
    "news_date", "news_category", "source_id", "citation_text", "verified_by",
    "verification_status", "confidence_level", "notes",
]

CURATED = {
    "phase1_palestine": [
        dict(metric="other", value=23, unit="persons", scope="EVT-001",
             headline="Weekly Gaza casualties: 23 Palestinians killed and 112 injured in the last week of June",
             summary="UN OCHA reported 23 Palestinians killed and 112 injured between 24 and 30 June 2026 in Gaza, citing the Gaza Ministry of Health.",
             url="https://www.ochaopt.org/content/humanitarian-situation-report-3-july-2026",
             date="2026-07-03", category="casualties", source="ocha_sitrep_3july",
             citation="OCHA's 3 July 2026 Humanitarian Situation Report documents 23 Palestinians killed, 1 body retrieved, 1 person died of wounds, and 112 injured between 24 and 30 June, citing MoH figures.",
             verified_by="ocha_sitrep_3july", status="verified", conf="high",
             notes="Linked to verified event EVT-001."),
        dict(metric="children_killed", value=1, unit="persons", scope="EVT-003",
             headline="Fifth-grade child dies from airstrike injuries near a learning space",
             summary="A fifth-grade child died from injuries sustained during an airstrike on 23 June near a temporary education learning space in Gaza.",
             url="https://www.ochaopt.org/content/humanitarian-situation-report-3-july-2026",
             date="2026-07-03", category="child impact", source="ocha_sitrep_3july",
             citation="OCHA reported that a fifth-grade child died from injuries sustained during an airstrike on 23 June near a temporary education learning space.",
             verified_by="ocha_sitrep_3july", status="verified", conf="high",
             notes="Linked to verified event EVT-003; child_flag set in persons per_003."),
        dict(metric="children_killed", value=1, unit="persons", scope="EVT-004",
             headline="17-year-old girl killed on way to high school exam",
             summary="A 17-year-old girl was killed by Israeli forces on her way to sit for a high school exam in the West Bank.",
             url="https://www.ochaopt.org/content/humanitarian-situation-report-3-july-2026",
             date="2026-07-03", category="child impact", source="ocha_sitrep_3july",
             citation="OCHA reported that Israeli forces killed three Palestinians (including one child) during raids and search operations in the West Bank between 23 and 29 June.",
             verified_by="ocha_sitrep_3july", status="verified", conf="high",
             notes="Linked to verified event EVT-004; child_flag set in persons per_004."),
        dict(metric="total_killed", value=1109, unit="persons", scope="EVT-031",
             headline="1,109 Palestinians killed in the West Bank since 7 October 2023",
             summary="Cumulative OCHA-recorded figure: 1,109 Palestinians (at least 243 children) killed in the West Bank including East Jerusalem between 7 October 2023 and 29 June 2026.",
             url="https://www.unrwa.org/resources/reports/unrwa-situation-report-229-humanitarian-crisis-gaza-strip-and-occupied-west-bank",
             date="2026-07-07", category="casualties", source="SRC-P007",
             citation="UNRWA Situation Report #229: 1,109 Palestinians (at least 243 of them children) killed in the West Bank including East Jerusalem between 7 October 2023 and 29 June 2026.",
             verified_by="SRC-P007", status="verified", conf="high",
             notes="Linked to verified event EVT-031."),
        dict(metric="total_killed", value=1053, unit="persons", scope="EVT-032",
             headline="1,053 fatalities recorded in Gaza since ceasefire despite continued strikes",
             summary="Cumulative figure from the 10 October 2025 ceasefire through 30 June 2026: 1,053 fatalities and 3,406 injuries from continued airstrikes, shelling, and gunfire.",
             url="https://www.unrwa.org/resources/reports/unrwa-situation-report-229-humanitarian-crisis-gaza-strip-and-occupied-west-bank",
             date="2026-07-07", category="casualties", source="SRC-P007",
             citation="UNRWA Situation Report #229: 1,053 fatalities and 3,406 injuries recorded from continued Israeli airstrikes, shelling, and gunfire despite the ceasefire.",
             verified_by="SRC-P007", status="verified", conf="high",
             notes="Linked to verified event EVT-032."),
        dict(metric="other", value=1, unit="persons", scope="EVT-029",
             headline="Aid logistics driver killed on Kerem Shalom to Gaza warehouse route",
             summary="A driver working for a World Central Kitchen logistics partner was killed by Israeli forces while transporting aid goods in an access-restricted area.",
             url="https://www.ochaopt.org/content/humanitarian-situation-report-10-july-2026",
             date="2026-07-10", category="humanitarian update", source="SRC-P006",
             citation="OCHA oPt Humanitarian Situation Report covering 29 June - 5 July 2026: a WCK logistics partner driver was killed while transporting aid goods in an access-restricted area.",
             verified_by="SRC-P006", status="verified", conf="medium",
             notes="Linked to verified event EVT-029; entity ENT-P1-05 World Central Kitchen."),
        dict(metric="other", value=1, unit="persons", scope="EVT-033",
             headline="Four-month-old infant dies after delayed transfer at Ramallah road gate",
             summary="A four-month-old Palestinian infant's transfer to hospital was delayed at an Israeli-staffed road gate near Ramallah; the infant later died at the hospital.",
             url="https://www.ochaopt.org/content/humanitarian-situation-report-10-july-2026",
             date="2026-07-10", category="child impact", source="SRC-P006",
             citation="OCHA oPt Humanitarian Situation Report covering 29 June - 5 July 2026: movement restrictions at an Israeli-staffed road gate near Ramallah delayed a four-month-old infant's hospital transfer.",
             verified_by="SRC-P006", status="verified", conf="medium",
             notes="Linked to verified event EVT-033."),
        dict(metric="other", value=0, unit="persons", scope="EVT-008",
             headline="Over 9,000 chickenpox cases recorded across 130 Gaza health facilities",
             summary="Deteriorating environmental conditions and overcrowding drove more than 9,000 chickenpox cases across 130+ health facilities in Gaza in two weeks.",
             url="https://www.ochaopt.org/content/humanitarian-situation-report-3-july-2026",
             date="2026-07-03", category="humanitarian update", source="ocha_sitrep_3july",
             citation="OCHA reported that in just two weeks, over 9,000 cases of chickenpox were recorded across more than 130 health facilities in Gaza.",
             verified_by="ocha_sitrep_3july", status="verified", conf="high",
             notes="Linked to verified event EVT-008."),
    ],
    "phase2_sudan": [
        dict(metric="other", value=42000, unit="persons", scope="EVT-021",
             headline="42,000 people assisted with a month of food across Al Obeid",
             summary="ICRC reported that 42,000 people were assisted with a month's worth of food across camps and urban settlements in Al Obeid.",
             url="https://www.icrc.org/en/where-we-work/sudan",
             date="2026-07-02", category="humanitarian update", source="icrc_sudan",
             citation="ICRC reported that 42,000 people were assisted with a month's worth of food across camps and urban settlements in Al Obeid.",
             verified_by="icrc_sudan", status="verified", conf="high",
             notes="Linked to verified event EVT-021."),
        dict(metric="children_killed", value=7000, unit="persons", scope="EVT-021",
             headline="Over 7,000 children and lactating women receive nutritional supplements",
             summary="Nutritional supplements were distributed to over 7,000 children and pregnant and lactating women in Al Obeid food assistance.",
             url="https://www.icrc.org/en/where-we-work/sudan",
             date="2026-07-02", category="child impact", source="icrc_sudan",
             citation="ICRC reported that nutritional supplements were distributed to over 7,000 children and pregnant and lactating women.",
             verified_by="icrc_sudan", status="verified", conf="high",
             notes="Linked to verified event EVT-021; child_flag set in persons per_007."),
        dict(metric="other", value=850, unit="persons", scope="EVT-022",
             headline="Over 850 weapon-wounded patients treated at Al Obeid Teaching Hospital",
             summary="More than 850 weapon-wounded patients were treated at Al Obeid Teaching Hospital since the beginning of the year.",
             url="https://www.icrc.org/en/where-we-work/sudan",
             date="2026-07-02", category="medical workers", source="icrc_sudan",
             citation="ICRC reported that more than 850 weapon-wounded patients were treated at Al Obeid Teaching Hospital since the beginning of the year.",
             verified_by="icrc_sudan", status="verified", conf="high",
             notes="Linked to verified event EVT-022; entity ENT-P2-06 Al Obeid Teaching Hospital."),
        dict(metric="other", value=6000, unit="persons", scope="EVT-023",
             headline="Cholera-prevention and sanitation activities for 6,000 displaced households",
             summary="ICRC documented cholera-prevention and sanitation activities for 6,000 displaced households in Al Obeid displacement sites.",
             url="https://www.icrc.org/en/where-we-work/sudan",
             date="2026-07-02", category="humanitarian update", source="icrc_sudan",
             citation="ICRC documented that cholera-prevention and sanitation activities are being conducted for 6,000 displaced households.",
             verified_by="icrc_sudan", status="verified", conf="high",
             notes="Linked to verified event EVT-023."),
        dict(metric="other", value=2400000, unit="persons", scope="EVT-030",
             headline="Rehabilitated water infrastructure to serve ~2.4 million in Khartoum",
             summary="Rehabilitated water pumps and treatment equipment are expected to provide safe water access to approximately 2.4 million people in Khartoum state.",
             url="https://www.icrc.org/en/where-we-work/sudan",
             date="2026-07-02", category="humanitarian update", source="icrc_sudan",
             citation="ICRC reported rehabilitation and donation of water pumps and treatment equipment expected to provide safe water access to approximately 2.4 million people in Khartoum state.",
             verified_by="icrc_sudan", status="verified", conf="high",
             notes="Linked to verified event EVT-030 (2025 impact summary)."),
        dict(metric="other", value=36, unit="persons", scope="EVT-025",
             headline="36 trained Red Crescent volunteers deployed across 12 displacement sites",
             summary="ICRC reported that 36 trained Red Crescent volunteers are deployed across 12 displacement sites in Al Obeid providing first aid.",
             url="https://www.icrc.org/en/where-we-work/sudan",
             date="2026-07-02", category="humanitarian update", source="icrc_sudan",
             citation="ICRC reported that 36 trained Red Crescent volunteers are deployed across 12 displacement sites in Al Obeid.",
             verified_by="icrc_sudan", status="verified", conf="high",
             notes="Linked to verified event EVT-025; entity ENT-P2-02 Sudanese Red Crescent."),
        dict(metric="other", value=0, unit="persons", scope="EVT-027",
             headline="ACLED records sustained heavy clashes in Khartoum with civilian displacement",
             summary="ACLED reported sustained heavy clashes in Khartoum resulting in large-scale displacement and reports of civilian casualties; exact figures vary across sources.",
             url="https://acleddata.com/",
             date="2026-07-12", category="casualties", source="acled_sudan_conf",
             citation="ACLED reported sustained heavy clashes in Khartoum resulting in large-scale displacement and reports of civilian casualties.",
             verified_by="acled_sudan_conf", status="estimated", conf="medium",
             notes="Linked to estimated event EVT-027."),
        dict(metric="other", value=0, unit="persons", scope="EVT-026",
             headline="Displaced families flee Al Fasher hostilities to Tawila town",
             summary="Hundreds of displaced families fled hostilities and violence in Al Fasher, seeking shelter in Tawila town in North Darfur.",
             url="https://www.icrc.org/en/where-we-work/sudan",
             date="2026-07-02", category="humanitarian update", source="icrc_sudan",
             citation="ICRC reported that hundreds of displaced families fled hostilities and violence in Al Fasher, seeking shelter in Tawila town.",
             verified_by="icrc_sudan", status="verified", conf="high",
             notes="Linked to verified event EVT-026."),
    ],
}


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [row for row in csv.DictReader(fh)]


def main():
    for phase, rows in CURATED.items():
        pdir = os.path.join(DATA, phase)
        news_path = os.path.join(pdir, "news_intelligence.csv")
        existing = load(news_path)
        # drop any previously-injected curated rows (those with a news_headline)
        existing = [r for r in existing if not (r.get("news_headline") or "").strip()]
        # renumber preserved auto rows cleanly
        n = 1
        for r in existing:
            r["news_id"] = f"NI-{n:03d}"
            n += 1
        for d in rows:
            row = {k: "" for k in FIELDS}
            row.update({
                "news_id": f"NI-{n:03d}",
                "legacy_record_id": "",
                "phase": phase,
                "country": existing[0].get("country", "") if existing else "",
                "conflict_name": existing[0].get("conflict_name", "") if existing else "",
                "metric": d["metric"],
                "value": d["value"],
                "unit": d["unit"],
                "event_or_person_scope": d["scope"],
                "news_headline": d["headline"],
                "news_summary": d["summary"],
                "news_source_url": d["url"],
                "news_date": d["date"],
                "news_category": d["category"],
                "source_id": d["source"],
                "citation_text": d["citation"],
                "verified_by": d["verified_by"],
                "verification_status": d["status"],
                "confidence_level": d["conf"],
                "notes": d["notes"],
            })
            existing.append(row)
            n += 1
        with open(news_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for r in existing:
                w.writerow({k: r.get(k, "") for k in FIELDS})
        print(f"[ok] {phase}: {len(existing)} rows ({len(rows)} curated + {len(existing)-len(rows)} auto)")


if __name__ == "__main__":
    main()
