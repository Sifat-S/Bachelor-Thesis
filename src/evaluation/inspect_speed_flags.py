
import csv
from pathlib import Path

FILE = (
    Path.home()
    / "Documents"
    / "Python"
    / "klaipeda_analysis"
    / "preprocessed_trajectories.csv"
)

print("===== FLAGGED GPS SEGMENTS =====")

flagged = []

with FILE.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        if row["large_speed_difference"] == "True":
            flagged.append(row)

print("Total flagged segments:", len(flagged))

for i, row in enumerate(flagged, start=1):
    print(f"\n===== SEGMENT {i} =====")

    for field in [
        "date",
        "trip_id",
        "vehicle",
        "route",
        "timestamp",
        "time_gap_seconds",
        "distance_metres",
        "gps_speed_kmh",
        "reported_speed_kmh",
        "speed_difference_kmh",
    ]:
        print(f"{field}: {row[field]}")

print("\nInspection completed.")
