
import csv
import math
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from statistics import median

# ========================================
# CONFIGURATION
# ========================================

DATA_FOLDER = (
    Path.home() / "Documents" / "Python"
    / "klaipeda_analysis"
)

INPUT_FILE = DATA_FOLDER / "moving_trajectories.csv"
OUTPUT_FILE = DATA_FOLDER / "preprocessed_trajectories.csv"

# Preliminary thresholds for investigation
MAX_GPS_SPEED_KMH = 120
MAX_SPEED_DIFFERENCE_KMH = 30

# ========================================
# HAVERSINE DISTANCE
# ========================================

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in metres."""
    radius = 6371000

    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.asin(
        min(1, math.sqrt(a))
    )


# ========================================
# READ DATA
# ========================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(INPUT_FILE)

trajectories = defaultdict(list)

with INPUT_FILE.open(
    "r", encoding="utf-8-sig", newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        try:
            timestamp = datetime.fromisoformat(
                row["matavimo_data"]
                + "T"
                + row["matavimo_laikas"]
            )

            lat = float(row["platuma_wgs"])
            lon = float(row["ilguma_wgs"])
            speed = float(row["greitis_kmh"])

            if not (-90 <= lat <= 90):
                continue

            if not (-180 <= lon <= 180):
                continue

            if not math.isfinite(speed):
                continue

            key = (
                row["matavimo_data"],
                row["reiso_id"],
                row["masinos_numeris"]
            )

            trajectories[key].append({
                "timestamp": timestamp,
                "latitude": lat,
                "longitude": lon,
                "reported_speed": speed,
                "route": row["marsrutas"],
                "trip_id": row["reiso_id"],
                "vehicle": row["masinos_numeris"]
            })

        except (ValueError, KeyError):
            continue

# ========================================
# PREPROCESS TRAJECTORIES
# ========================================

results = []

summary = {
    "valid_segments": 0,
    "invalid_time_intervals": 0,
    "suspicious_gps_speeds": 0,
    "large_speed_differences": 0
}

for key, records in trajectories.items():

    records.sort(key=lambda r: r["timestamp"])

    for previous, current in zip(
        records, records[1:]
    ):

        seconds = (
            current["timestamp"]
            - previous["timestamp"]
        ).total_seconds()

        if seconds <= 0:
            summary["invalid_time_intervals"] += 1
            continue

        distance_m = haversine(
            previous["latitude"],
            previous["longitude"],
            current["latitude"],
            current["longitude"]
        )

        gps_speed = (distance_m / seconds) * 3.6

        # Compare implied GPS speed against reported speed
        speed_difference = abs(
            gps_speed - current["reported_speed"]
        )

        suspicious_speed = (
            gps_speed > MAX_GPS_SPEED_KMH
        )

        large_difference = (
            speed_difference > MAX_SPEED_DIFFERENCE_KMH
        )

        if suspicious_speed:
            summary["suspicious_gps_speeds"] += 1

        if large_difference:
            summary["large_speed_differences"] += 1

        summary["valid_segments"] += 1

        results.append({
            "date": key[0],
            "trip_id": key[1],
            "vehicle": key[2],
            "route": current["route"],
            "timestamp": current["timestamp"].isoformat(),
            "latitude": current["latitude"],
            "longitude": current["longitude"],
            "time_gap_seconds": seconds,
            "distance_metres": round(distance_m, 2),
            "gps_speed_kmh": round(gps_speed, 2),
            "reported_speed_kmh": current["reported_speed"],
            "speed_difference_kmh": round(speed_difference, 2),
            "suspicious_gps_speed": suspicious_speed,
            "large_speed_difference": large_difference
        })

# ========================================
# SAVE PROCESSED RESULTS
# ========================================

if results:
    with OUTPUT_FILE.open(
        "w", encoding="utf-8", newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

# ========================================
# PRINT SUMMARY
# ========================================

print("===== KLAIPEDA GPS PREPROCESSING =====")

print("Trajectory groups:", len(trajectories))
print("Input observations:",
      sum(len(v) for v in trajectories.values()))

print("Valid segments:",
      summary["valid_segments"])

print("Invalid/duplicate time intervals:",
      summary["invalid_time_intervals"])

print("Segments above 120 km/h:",
      summary["suspicious_gps_speeds"])

print("Speed differences above 30 km/h:",
      summary["large_speed_differences"])

if results:
    gps_speeds = [
        r["gps_speed_kmh"] for r in results
    ]

    print(
        "Median GPS-derived speed:",
        round(median(gps_speeds), 2),
        "km/h"
    )

print("\nOutput file:", OUTPUT_FILE)
print("Original CSV was not modified.")
