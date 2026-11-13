
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ======================================
# 1. CONFIGURATION
# ======================================

DATA_FOLDER = (
    Path.home()
    / "Documents"
    / "Python"
    / "klaipeda_analysis"
)

INPUT_FILE = DATA_FOLDER / "preprocessed_trajectories.csv"
OUTPUT_FILE = DATA_FOLDER / "isolation_forest_results.csv"
PLOT_FILE = DATA_FOLDER / "isolation_forest_anomalies.png"

RANDOM_STATE = 42

# Exploratory setting: expect approximately
# 2% of observations to be flagged.
CONTAMINATION = 0.02

FEATURES = [
    "gps_speed_kmh",
    "reported_speed_kmh",
    "speed_difference_kmh",
    "distance_metres",
    "time_gap_seconds"
]

# ======================================
# 2. LOAD DATA
# ======================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Processed CSV not found: {INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

print("===== ISOLATION FOREST ANALYSIS =====")
print("Total input segments:", len(df))

# Ensure features are numeric
for feature in FEATURES:
    df[feature] = pd.to_numeric(
        df[feature],
        errors="coerce"
    )

# Keep only rows with complete features
df = df.dropna(subset=FEATURES).copy()

print("Segments used for training:", len(df))

if len(df) < 10:
    raise ValueError("Not enough valid observations.")

# ======================================
# 3. FEATURE PREPARATION
# ======================================

X = df[FEATURES]

# Standardise features for comparison
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ======================================
# 4. TRAIN ISOLATION FOREST
# ======================================

model = IsolationForest(
    n_estimators=200,
    contamination=CONTAMINATION,
    random_state=RANDOM_STATE,
    n_jobs=-1
)

model.fit(X_scaled)

# Prediction:
#  1 = normal
# -1 = anomaly
df["prediction"] = model.predict(X_scaled)

# Lower scores indicate more unusual data
df["anomaly_score"] = model.score_samples(X_scaled)

df["anomaly_label"] = df["prediction"].map({
    1: "Normal",
    -1: "Anomaly"
})

# ======================================
# 5. RESULTS
# ======================================

normal = df[df["prediction"] == 1]
anomalies = df[df["prediction"] == -1]

print("\n===== DETECTION RESULTS =====")

print("Normal segments:", len(normal))
print("Flagged anomalies:", len(anomalies))

print(
    "Flagged percentage:",
    round(len(anomalies) / len(df) * 100, 2),
    "%"
)

print("\n===== MOST UNUSUAL SEGMENTS =====")

columns = [
    "date",
    "timestamp",
    "route",
    "gps_speed_kmh",
    "reported_speed_kmh",
    "speed_difference_kmh",
    "anomaly_score"
]

print(
    anomalies.sort_values("anomaly_score")
    [columns]
    .head(10)
    .to_string(index=False)
)

# ======================================
# 6. SAVE RESULTS
# ======================================

df.to_csv(OUTPUT_FILE, index=False)

# ======================================
# 7. VISUALISE RESULTS
# ======================================

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(
    normal["gps_speed_kmh"],
    normal["reported_speed_kmh"],
    s=15,
    alpha=0.5,
    label="Normal"
)

ax.scatter(
    anomalies["gps_speed_kmh"],
    anomalies["reported_speed_kmh"],
    s=55,
    marker="x",
    color="red",
    label="Flagged anomaly"
)

ax.set_title("Isolation Forest - Klaipeda GPS Segments")
ax.set_xlabel("GPS-derived speed (km/h)")
ax.set_ylabel("Reported speed (km/h)")
ax.grid(True, alpha=0.3)
ax.legend()

fig.tight_layout()
fig.savefig(PLOT_FILE, dpi=180)
plt.close(fig)

print("\n===== OUTPUT FILES =====")
print("Results CSV:", OUTPUT_FILE)
print("Visualisation:", PLOT_FILE)

print("\nAnalysis completed.")
print("Original processed CSV was not modified.")
