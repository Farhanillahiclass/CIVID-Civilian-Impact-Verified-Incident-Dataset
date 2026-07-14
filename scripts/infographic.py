"""
CIVID Real-time Visualization & Infographic Generator
====================================================
Generates key visual graphics directly from production CSVs (events.csv).
Saves a clean PNG summary image for the repository and launches an interactive viewer.

Usage:
    python scripts/infographic.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1. Paths set up
ROOT = Path(__file__).resolve().parent.parent
phase_paths = {
    "Palestine/Gaza": ROOT / "data" / "phase1_palestine" / "events.csv",
    "Sudan": ROOT / "data" / "phase2_sudan" / "events.csv",
}

print("[processing] Loading datasets to build real-time infographic...")

# 2. Extract and combine production events safely
loaded_dfs = []
for phase_name, fpath in phase_paths.items():
    if fpath.exists():
        try:
            df = pd.read_csv(fpath)
            df["phase_name"] = phase_name
            loaded_dfs.append(df)
        except Exception as e:
            print(f"[error] Failed to parse data from {fpath}: {e}")

if not loaded_dfs:
    print("[error] No active production events.csv data files found to visualize!")
    exit(1)

all_events = pd.concat(loaded_dfs, ignore_index=True)

# 3. Handle data cleanup and type constraints
numeric_metrics = ["fatalities", "injuries", "missing"]
for col in numeric_metrics:
    if col in all_events.columns:
        all_events[col] = pd.to_numeric(all_events[col], errors="coerce").fillna(0)
    else:
        all_events[col] = 0.0

if "verification_status" not in all_events.columns:
    all_events["verification_status"] = "unverified"
if "confidence_level" not in all_events.columns:
    all_events["confidence_level"] = "low"

# Ensure verification categories are formatted nicely
all_events["verification_status"] = all_events["verification_status"].str.title()
all_events["confidence_level"] = all_events["confidence_level"].str.upper()

# 4. Canvas Creation & Styling
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("CIVID - REAL-TIME DATA QUALITY & IMPACT INSIGHTS", fontsize=18, fontweight="bold", color="#1a202c", y=1.02)

# --- PANEL 1: Humanitarian Figures ---
figures_df = all_events.groupby("phase_name")[numeric_metrics].sum().reset_index()
melted_df = figures_df.melt(id_vars="phase_name", var_name="Metric", value_name="Count")

sns.barplot(
    ax=axes[0],
    data=melted_df,
    x="phase_name",
    y="Count",
    hue="Metric",
    palette="muted",
    edgecolor="black",
    linewidth=0.7
)
axes[0].set_title("Reported Human Cost Metrics", fontsize=13, fontweight="bold", pad=10)
axes[0].set_xlabel("Operational Area", fontweight="bold")
axes[0].set_ylabel("Aggregated Casualties Count", fontweight="bold")
axes[0].legend(title="Indicators")

# --- PANEL 2: Data Validation Status ---
verify_stats = all_events["verification_status"].value_counts().reset_index()
verify_stats.columns = ["Status", "Record Count"]

sns.barplot(
    ax=axes[1],
    data=verify_stats,
    x="Status",
    y="Record Count",
    palette="Blues_r",
    edgecolor="black",
    linewidth=0.7
)
axes[1].set_title("Dataset Verification State", fontsize=13, fontweight="bold", pad=10)
axes[1].set_xlabel("Audit Status", fontweight="bold")
axes[1].set_ylabel("Records", fontweight="bold")

# --- PANEL 3: Source Trust Metrics ---
conf_stats = all_events["confidence_level"].value_counts().reset_index()
conf_stats.columns = ["Confidence", "Record Count"]

sns.barplot(
    ax=axes[2],
    data=conf_stats,
    x="Confidence",
    y="Record Count",
    palette="YlOrRd_r",
    edgecolor="black",
    linewidth=0.7
)
axes[2].set_title("Source Trust Classifications", fontsize=13, fontweight="bold", pad=10)
axes[2].set_xlabel("Confidence Classification", fontweight="bold")
axes[2].set_ylabel("Records", fontweight="bold")

# Save high quality PNG preview for your repo assets
output_img = ROOT / "data" / "staging" / "live_dashboard_preview.png"
output_img.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(output_img, dpi=300, bbox_inches="tight")
print(f"[ok] Infographic PNG generated successfully and saved at: {output_img}")

# Show UI
plt.show()