
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CSV_PATH = Path(
    r"C:\Downloads\KlaipedaViesasisTransportas.csv"
)

# Three actual trip groups from our previous analysis
TARGET_TRIPS = {
    ("2026-06-08", "A115-01-1-260608-b2a-0750", "B1385 kmte"),
    ("2026-06-06", "A14-03-6-251115-ab-0830", "819 kte"),
    ("2026-05-28", "A115-01-1-251119-ab-0610", "B1385 kmte"),
}

observations = defaultdict(list)
total_rows = 0

print("Searching full Klaipeda GPS dataset...")

with CSV_PATH.open(
    "r", encoding="utf-8-sig", newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        total_rows += 1

        key = (
            row["matavimo_data"],
            row["reiso_id"],
            row["masinos_numeris"]
        )

        if key not in TARGET_TRIPS:
            continue

        try:
            timestamp = datetime.fromisoformat(
                row["matavimo_data"]
                + "T"
                + row["matavimo_laikas"]
            )

            observations[key].append({
                "time": timestamp,
                "lat": float(row["platuma_wgs"]),
                "lon": float(row["ilguma_wgs"]),
                "speed": float(row["greitis_kmh"])
            })

        except (ValueError, TypeError):
            continue

print("\n===== FULL DATASET RESULTS =====")
print("Total CSV records scanned:", total_rows)

for key in sorted(TARGET_TRIPS):
    positions = sorted(
        observations[key],
        key=lambda x: x["time"]
    )

    print("\n----------------------------")
    print("Date:", key[0])
    print("Trip ID:", key[1])
    print("Vehicle:", key[2])
    print("Total observations:", len(positions))

    if positions:
        print("First timestamp:", positions[0]["time"])
        print("Last timestamp:", positions[-1]["time"])

        gaps = [
            (b["time"] - a["time"]).total_seconds()
            for a, b in zip(positions, positions[1:])
        ]

        if gaps:
            print("Median gap (seconds):",
                  sorted(gaps)[len(gaps) // 2])
            print("Largest gap (seconds):", max(gaps))

        print("\nFirst 3 observations:")

        for position in positions[:3]:
            print(position)

print("\nAnalysis completed.")
print("Original CSV was not modified.")
