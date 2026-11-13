
import csv
from pathlib import Path
from collections import Counter, defaultdict

# Location of the downloaded dataset
CSV_PATH = Path(
    r"C:\Downloads\KlaipedaViesasisTransportas.csv"
)

SAMPLE_SIZE = 100_000

if not CSV_PATH.exists():
    print("ERROR: CSV file not found.")
    print("Expected location:", CSV_PATH)
    raise SystemExit(1)

print("===== KLAIPEDA GPS DATASET ANALYSIS =====")
print(f"File: {CSV_PATH.name}")
print(f"Size: {CSV_PATH.stat().st_size / 1024**3:.2f} GB")

total_rows = 0
missing = Counter()
vehicles = set()
routes = set()
trips = set()
trip_counts = Counter()
dates = []
invalid_coordinates = 0
invalid_speeds = 0
valid_locations = 0
speeds = []

important_columns = [
    "masinos_numeris",
    "marsrutas",
    "reiso_id",
    "ilguma_wgs",
    "platuma_wgs",
    "greitis_kmh",
    "matavimo_data",
    "matavimo_laikas",
    "nuokrypis_sekundemis",
]

with CSV_PATH.open(
    "r", encoding="utf-8-sig", newline=""
) as file:

    reader = csv.DictReader(file)

    print("\nTotal columns:", len(reader.fieldnames or []))
    print("Columns:", reader.fieldnames)

    for row in reader:
        if total_rows >= SAMPLE_SIZE:
            break

        total_rows += 1

        for column in important_columns:
            if not (row.get(column) or "").strip():
                missing[column] += 1

        vehicle = (row.get("masinos_numeris") or "").strip()
        route = (row.get("marsrutas") or "").strip()
        trip = (row.get("reiso_id") or "").strip()
        date = (row.get("matavimo_data") or "").strip()

        if vehicle:
            vehicles.add(vehicle)

        if route:
            routes.add(route)

        if trip:
            trips.add(trip)

            # Count observations from the same journey
            trip_key = (date, trip, vehicle)
            trip_counts[trip_key] += 1

        if date:
            dates.append(date)

        # Check GPS coordinates
        try:
            lat = float(row["platuma_wgs"])
            lon = float(row["ilguma_wgs"])

            if  -90 <= lat <= 90 and -180 <= lon <= 180:
                valid_locations += 1
            else:
                invalid_coordinates += 1

        except (ValueError, TypeError, KeyError):
            invalid_coordinates += 1

        # Check vehicle speed
        try:
            speed = float(row["greitis_kmh"])

            if 0 <= speed <= 200:
                speeds.append(speed)
            else:
                invalid_speeds += 1

        except (ValueError, TypeError, KeyError):
            invalid_speeds += 1


print("\n===== ANALYSIS RESULTS =====")

print("Records analysed:", total_rows)
print("Unique vehicles:", len(vehicles))
print("Unique routes:", len(routes))
print("Unique trip IDs:", len(trips))

if dates:
    print("Earliest date in sample:", min(dates))
    print("Latest date in sample:", max(dates))

print("\n===== DATA QUALITY =====")
print("Valid GPS coordinates:", valid_locations)
print("Invalid/missing GPS coordinates:", invalid_coordinates)
print("Invalid/missing speed values:", invalid_speeds)

if speeds:
    print("Minimum speed:", min(speeds), "km/h")
    print("Maximum speed:", max(speeds), "km/h")
    print(
        "Average speed:",
        round(sum(speeds) / len(speeds), 2),
        "km/h"
    )

print("\n===== MISSING VALUES =====")

for column in important_columns:
    count = missing[column]
    percentage = (count / total_rows * 100) if total_rows else 0
    print(f"{column}: {count} ({percentage:.2f}%)")

print("\n===== TRAJECTORY POTENTIAL =====")

repeated_trips = sum(
    1 for count in trip_counts.values() if count >= 2
)

longer_trips = sum(
    1 for count in trip_counts.values() if count >= 10
)

print("Trip groups:", len(trip_counts))
print("Trip groups with 2+ observations:", repeated_trips)
print("Trip groups with 10+ observations:", longer_trips)

print("\nTop 5 trip groups by observation count:")

for trip_key, count in trip_counts.most_common(5):
    print(f"{trip_key}: {count} observations")

print("\n===== ANALYSIS COMPLETED =====")
print("The original CSV was not modified.")
