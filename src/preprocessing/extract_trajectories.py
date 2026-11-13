
import csv
from pathlib import Path
from collections import Counter

# Original dataset
INPUT_FILE = Path(
    r"C:\Downloads\KlaipedaViesasisTransportas.csv"
)

# Folder for extracted data
OUTPUT_FOLDER = Path(
    r"C:\Users\sifat\Documents\Python\klaipeda_analysis"
)

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_FOLDER / "moving_trajectories.csv"

# Two previously identified moving journeys
TARGET_TRIPS = {
    ("2026-05-28", "A115-01-1-251119-ab-0610", "B1385 kmte"),
    ("2026-06-08", "A115-01-1-260608-b2a-0750", "B1385 kmte"),
}

columns = [
    "matavimo_data",
    "matavimo_laikas",
    "masinos_numeris",
    "marsrutas",
    "reiso_id",
    "platuma_wgs",
    "ilguma_wgs",
    "greitis_kmh",
    "azimutas",
    "nuokrypis_sekundemis",
]

counts = Counter()

print("Extracting selected GPS trajectories...")

with INPUT_FILE.open(
    "r", encoding="utf-8-sig", newline=""
) as source, OUTPUT_FILE.open(
    "w", encoding="utf-8", newline=""
) as destination:

    reader = csv.DictReader(source)
    writer = csv.DictWriter(
        destination,
        fieldnames=columns
    )

    writer.writeheader()

    for row in reader:
        key = (
            row["matavimo_data"],
            row["reiso_id"],
            row["masinos_numeris"],
        )

        if key not in TARGET_TRIPS:
            continue

        writer.writerow({
            col: row.get(col, "")
            for col in columns
        })

        counts[key] += 1

print("\n===== EXTRACTION RESULTS =====")

for key in sorted(TARGET_TRIPS):
    print(f"\nDate: {key[0]}")
    print(f"Trip: {key[1]}")
    print(f"Vehicle: {key[2]}")
    print(f"Observations: {counts[key]}")

print("\nTotal extracted:", sum(counts.values()))
print("Output file:", OUTPUT_FILE)
print("\nExtraction completed.")
