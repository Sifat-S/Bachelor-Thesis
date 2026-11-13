
import csv
from pathlib import Path
from datetime import datetime
from statistics import median

CSV_PATH = Path(
    r"C:\Downloads\KlaipedaViesasisTransportas.csv"
)

TARGET_DATE = "2026-06-06"
TARGET_TRIP = "A14-03-6-251115-ab-0830"
TARGET_VEHICLE = "819 kte"

records = []

with CSV_PATH.open(
    "r", encoding="utf-8-sig", newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        if (
            row["matavimo_data"] != TARGET_DATE
            or row["reiso_id"] != TARGET_TRIP
            or row["masinos_numeris"] != TARGET_VEHICLE
        ):
            continue

        try:
            timestamp = datetime.fromisoformat(
                row["matavimo_data"]
                + "T"
                + row["matavimo_laikas"]
            )

            records.append({
                "time": timestamp,
                "latitude": float(row["platuma_wgs"]),
                "longitude": float(row["ilguma_wgs"]),
                "speed": float(row["greitis_kmh"]),
            })

        except ValueError:
            continue

records.sort(key=lambda r: r["time"])

# Analyse speeds for the selected vehicle
moving = [r for r in records if r["speed"] > 0]
stationary = [r for r in records if r["speed"] == 0]

print("\n===== MOVEMENT ANALYSIS =====")

print("Total observations:", len(records))
print("Stationary observations:", len(stationary))
print("Moving observations:", len(moving))

if records:
    print(
        "Stationary percentage:",
        round(len(stationary) / len(records) * 100, 2),
        "%"
    )

    print(
        "Maximum reported speed:",
        max(r["speed"] for r in records),
        "km/h"
    )

    latitudes = [r["latitude"] for r in records]
    longitudes = [r["longitude"] for r in records]

    print("Latitude range:", min(latitudes), max(latitudes))
    print("Longitude range:", min(longitudes), max(longitudes))

if moving:
    print("\nFirst 5 moving observations:")
    for r in moving[:5]:
        print(r)
else:
    print("\nNo movement reported in this trip group.")

print("===== TRIP TIMELINE INSPECTION =====")
print("Observations:", len(records))

if records:
    print("Start:", records[0]["time"])
    print("End:", records[-1]["time"])

gaps = [
    (b["time"] - a["time"]).total_seconds()
    for a, b in zip(records, records[1:])
]

if gaps:
    print("Median interval:", median(gaps), "seconds")
    print("Largest interval:", max(gaps), "seconds")

    print("Gaps over 5 minutes:",
          sum(gap > 300 for gap in gaps))

print("\n===== HOURLY OBSERVATIONS =====")

hourly_counts = {}

for record in records:
    hour = record["time"].strftime("%H:00")
    hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

for hour, count in sorted(hourly_counts.items()):
    print(f"{hour}: {count} observations")

print("\n===== SAMPLE MOVEMENT =====")

for record in records[::max(1, len(records) // 12)][:13]:
    print(
        record["time"],
        "Lat:", record["latitude"],
        "Lon:", record["longitude"],
        "Speed:", record["speed"]
    )

print("\nInspection completed.")
