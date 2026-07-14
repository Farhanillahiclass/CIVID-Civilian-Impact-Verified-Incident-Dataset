"""
CIVID Detailed Dataset Factsheet Generator
=========================================
Extracts deep structural metadata and statistics across all phases and 
creates a highly detailed textual and visual infographic overview poster.

Usage:
    python scripts/detailed_factsheet.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Paths Setup
ROOT = Path(__file__).resolve().parent.parent
phase_paths = {
    "Palestine/Gaza (Phase 1)": {
        "events": ROOT / "data" / "phase1_palestine" / "events.csv",
        "sources": ROOT / "data" / "phase1_palestine" / "sources.csv"
    },
    "Sudan (Phase 2)": {
        "events": ROOT / "data" / "phase2_sudan" / "events.csv",
        "sources": ROOT / "data" / "phase2_sudan" / "sources.csv"
    }
}

print("[processing] Extracting deep metadata for the Detailed Factsheet...")

# Data containers
stats_summary = []

# 2. Extract detailed analytics
for phase_name, paths in phase_paths.items():
    events_file = paths["events"]
    sources_file = paths["sources"]
    
    events_count = 0
    sources_count = 0
    total_fatalities = 0
    total_injuries = 0
    verified_percentage = 0.0
    date_range = "N/A"
    top_sources = []
    
    # Process Events
    if events_file.exists():
        try:
            df_evt = pd.read_csv(events_file)
            events_count = len(df_evt)
            
            # Fatalities & Injuries Sum
            if "fatalities" in df_evt.columns:
                total_fatalities = int(pd.to_numeric(df_evt["fatalities"], errors="coerce").fillna(0).sum())
            if "injuries" in df_evt.columns:
                total_injuries = int(pd.to_numeric(df_evt["injuries"], errors="coerce").fillna(0).sum())
                
            # Date Range calculation
            if "event_date" in df_evt.columns and not df_evt["event_date"].dropna().empty:
                dates = pd.to_datetime(df_evt["event_date"], errors="coerce").dropna()
                if not dates.empty:
                    date_range = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
            
            # Verification percentage
            if "verification_status" in df_evt.columns and events_count > 0:
                verified_runs = df_evt["verification_status"].str.lower() == "verified"
                verified_percentage = (verified_runs.sum() / events_count) * 100
                
        except Exception as e:
            print(f"[error] Failed processing events for {phase_name}: {e}")
            
    # Process Sources
    if sources_file.exists():
        try:
            df_src = pd.read_csv(sources_file)
            sources_count = len(df_src)
            if "source_name" in df_src.columns:
                top_sources = df_src["source_name"].value_counts().head(3).index.tolist()
        except Exception as e:
            print(f"[error] Failed processing sources for {phase_name}: {e}")
            
    stats_summary.append({
        "phase": phase_name,
        "events": events_count,
        "sources": sources_count,
        "fatalities": total_fatalities,
        "injuries": total_injuries,
        "span": date_range,
        "verified_ratio": verified_percentage,
        "top_publishers": ", ".join(top_sources) if top_sources else "None registered"
    })

# 3. Draw Factsheet Infographic (Canvas)
fig, ax = plt.subplots(figsize=(12, 10))
ax.axis("off")  # Turn off standard axis

# Styling variables
title_color = "#1a365d"
section_header_color = "#2b6cb0"
text_color = "#2d3748"
card_background = "#f7fafc"

# Draw Background Card
rect = plt.Rectangle((0, 0), 1, 1, fill=True, color=card_background, transform=ax.transAxes, zorder=-1)
ax.add_patch(rect)

# Add Outer Border
border = plt.Rectangle((0.01, 0.01), 0.98, 0.98, fill=False, color="#cbd5e0", linewidth=3, transform=ax.transAxes)
ax.add_patch(border)

# Top Banner Title
plt.text(0.5, 0.92, "CIVID DATASET COMPREHENSIVE FACTSHEET", 
         fontsize=20, fontweight="bold", color=title_color, ha="center", transform=ax.transAxes)
plt.text(0.5, 0.89, f"Generated Real-time on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", 
         fontsize=11, style="italic", color="#718096", ha="center", transform=ax.transAxes)

# Decorative separator line
ax.plot([0.05, 0.95], [0.87, 0.87], color="#cbd5e0", transform=ax.transAxes, linewidth=1.5)

# Text Coordinates Init
y_offset = 0.80

for item in stats_summary:
    # Phase Title Banner
    plt.text(0.05, y_offset, f"📍 AREA/PHASE: {item['phase'].upper()}", 
             fontsize=14, fontweight="bold", color=section_header_color, transform=ax.transAxes)
    y_offset -= 0.04
    
    # Left Column: Volume Data
    vol_text = (
        f"• Total Logged Events  : {item['events']} incidents\n"
        f"• Registered Sources    : {item['sources']} tracked sources\n"
        f"• Data Verification %  : {item['verified_ratio']:.1f}% Verified\n"
        f"• Temporal Range        : {item['span']}"
    )
    plt.text(0.08, y_offset, vol_text, fontsize=11.5, color=text_color, linespacing=1.6, transform=ax.transAxes, va="top")
    
    # Right Column: Human Cost & Metadata
    meta_text = (
        f"• Total Recorded Fatalities : {item['fatalities']:,} deaths\n"
        f"• Total Recorded Injuries   : {item['injuries']:,} injured\n"
        f"• Main Data Providers       : {item['top_publishers']}"
    )
    plt.text(0.55, y_offset, meta_text, fontsize=11.5, color=text_color, linespacing=1.6, transform=ax.transAxes, va="top")
    
    # Adjust spacing for next card group
    y_offset -= 0.22
    ax.plot([0.05, 0.95], [y_offset + 0.04, y_offset + 0.04], color="#e2e8f0", transform=ax.transAxes, linewidth=1, linestyle="--")

# Global Dataset Insights Footer
plt.text(0.05, y_offset, "🔍 GENERAL PIPELINE INTEGRITY NOTE:", 
         fontsize=12, fontweight="bold", color="#2c5282", transform=ax.transAxes)
y_offset -= 0.03

integrity_note = (
    "This infographic shows verified + auto-promoted unverified data points directly from production tracks.\n"
    "Unverified entries remain at 'low' confidence status until manual validation updates target fields inside database."
)
plt.text(0.08, y_offset, integrity_note, fontsize=10.5, style="italic", color="#4a5568", linespacing=1.4, transform=ax.transAxes, va="top")

# Save Infographic Image
output_img = ROOT / "data" / "staging" / "dataset_factsheet.png"
output_img.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_img, dpi=300, bbox_inches="tight")
print(f"[ok] Detailed Factsheet infographic saved at: {output_img}")

# Display UI
plt.show()