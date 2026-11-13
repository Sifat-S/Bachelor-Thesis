
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import matplotlib.pyplot as plt

# Extracted GPS dataset
INPUT_FILE = Path(
    r"C:\Users\sifat\Documents\Python"
    r"\klaipeda_analysis\moving_trajectories.csv"
)

OUTPUT_FOLDER = INPUT_FILE.parent

trajectories = defaultdict(list)

print("Reading GPS observations...")

# Read extracted CSV
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

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue

            key = (
                row["matavimo_data"],
                row["reiso_id"],
                row["masinos_numeris"]
            )

            trajectories[key].append({
                "time": timestamp,
                "lat": lat,
                "lon": lon,
                "speed": speed
            })

        except (ValueError, KeyError):
            continue

print("\n===== OFFLINE GPS VISUALISATION =====")

for key, observations in sorted(trajectories.items()):

    if not observations:
        continue

    date, trip_id, vehicle = key

    observations.sort(key=lambda x: x["time"])

    latitudes = [r["lat"] for r in observations]
    longitudes = [r["lon"] for r in observations]
    speeds = [r["speed"] for r in observations]

    fig, ax = plt.subplots(figsize=(10, 8))

    # Connect GPS points chronologically
    ax.plot(
        longitudes,
        latitudes,
        color="royalblue",
        linewidth=1.5,
        alpha=0.8,
        label="GPS trajectory"
    )

    # Mark first and last positions
    ax.scatter(
        longitudes[0],
        latitudes[0],
        color="green",
        s=90,
        zorder=5,
        label="Start"
    )

    ax.scatter(
        longitudes[-1],
        latitudes[-1],
        color="red",
        s=90,
        zorder=5,
        label="End"
    )

    # Show GPS positions coloured by reported speed
    points = ax.scatter(
        longitudes,
        latitudes,
        c=speeds,
        cmap="viridis",
        s=12,
        alpha=0.75,
        zorder=3
    )

    fig.colorbar(
        points,
        ax=ax,
        label="Reported speed (km/h)"
    )

    ax.set_title(
        f"Klaipeda GPS Trajectory\n"
        f"Date: {date} | Vehicle: {vehicle}"
    )

    ax.set_xlabel("Longitude (WGS84)")
    ax.set_ylabel("Latitude (WGS84)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Preserve approximate geographic proportions
    mean_lat = sum(latitudes) / len(latitudes)
    ax.set_aspect(
        1 / max(0.01, abs(__import__("math").cos(
            __import__("math").radians(mean_lat)
        ))),
        adjustable="datalim"
    )

    fig.tight_layout()

    output_file = (
        OUTPUT_FOLDER / f"trajectory_offline_{date}.png"
    )

    fig.savefig(output_file, dpi=180)
    plt.close(fig)

    print(f"\nDate: {date}")
    print(f"Vehicle: {vehicle}")
    print(f"Observations: {len(observations)}")
    print(f"Minimum speed: {min(speeds)} km/h")
    print(f"Maximum speed: {max(speeds)} km/h")
    print(f"Saved: {output_file}")

print("\nOffline visualisation completed.")
