# Dataset Selection and Justification

## 1. Thesis Topic

**Automated Anomaly Detection and Threat Intelligence in Urban Logistics and Transport**

## 2. Selected Dataset

The primary dataset selected for this bachelor's thesis is **Historical Klaipėda Public Transport GPS Data**, obtained from the Lithuanian Open Data Portal.

**Dataset information:**

- Source: https://data.gov.lt/datasets/3856/
- Resource: `KlaipedaViesasisTransportas`
- File format: CSV
- Downloaded file size: 2.03 GB
- Total observations: 7,347,211
- Number of columns: 20
- Geographic focus: Klaipėda region, Lithuania

## 3. Dataset Description

The dataset contains historical GPS and operational telemetry observations from public transport vehicles.

Relevant attributes include:

| Attribute | Description |
|---|---|
| `masinos_numeris` | Vehicle identifier |
| `marsrutas` | Route identifier |
| `reiso_id` | Trip identifier |
| `platuma_wgs` | GPS latitude |
| `ilguma_wgs` | GPS longitude |
| `greitis_kmh` | Reported vehicle speed |
| `azimutas` | Vehicle heading |
| `matavimo_data` | Measurement date |
| `matavimo_laikas` | Measurement time |
| `nuokrypis_sekundemis` | Schedule deviation in seconds |

These attributes support spatial-temporal analysis of public transport movement.

## 4. Preliminary Data Quality Assessment

An initial analysis was performed on 100,000 observations.

Results:

- Unique vehicles: 246
- Unique routes: 70
- Unique trip identifiers: 11,208
- Valid coordinate values: 100%
- Missing trip identifiers: 1.01%
- Missing schedule-deviation values: 0.11%
- Average reported speed: 26.54 km/h
- Observed sample date range: May 26 to June 14, 2026

These findings describe the initial sample and should not be interpreted as statistics for the complete dataset.

## 5. Trajectory Reconstruction

Three selected vehicle-trip groups were examined across the complete CSV.

| Date | GPS observations | Median recording interval |
|---|---:|---:|
| May 28, 2026 | 476 | 10 seconds |
| June 6, 2026 | 903 | 40 seconds |
| June 8, 2026 | 549 | 10 seconds |

The June 6 group contained 903 stationary observations. The other two groups represented moving vehicle trajectories.

The moving trajectories were extracted and visualised successfully, confirming that the dataset can support trajectory reconstruction.

## 6. Preliminary Preprocessing Results

Two moving trajectories containing 1,025 observations were processed.

Results:

- Valid movement segments: 1,023
- Invalid or duplicate time intervals: 0
- GPS-derived speeds exceeding the exploratory 120 km/h threshold: 0
- Segments with reported-versus-derived speed differences above 30 km/h: 2
- Median GPS-derived speed: 46.37 km/h

The identified speed discrepancies require interpretation and are not automatically classified as genuine anomalies.

## 7. Initial Anomaly Detection Experiment

An exploratory Isolation Forest model was trained using 1,023 processed segments.

Features included GPS-derived speed, reported speed, speed difference, distance between observations, and recording time interval.

The model flagged 21 segments (2.05%) with a contamination setting of 0.02.

These are preliminary model predictions. No ground-truth labels were available to confirm whether the flagged segments represent real operational anomalies.

## 8. Dataset Selection Justification

The dataset was selected because it provides:

1. Historical vehicle movement observations.
2. GPS coordinates and timestamps suitable for spatial-temporal analysis.
3. Vehicle, route and trip identifiers.
4. Speed and schedule-deviation attributes.
5. Repeated measurements that support trajectory reconstruction.
6. Sufficient data volume for further machine-learning experiments.

Initial preprocessing and Isolation Forest experiments demonstrated technical feasibility.

## 9. Limitations and Future Work

The preliminary experiments used only a small number of selected trajectories. Additional research is required to assess data quality across more routes, vehicles and dates.

Future work will include representative sampling, movement segmentation, handling stationary observations, anomaly-detection model comparison, and computational performance evaluation.

Precision and recall will require a defensible reference-labelling or controlled anomaly-injection approach.

GPS and operational irregularities will not automatically be interpreted as security threats without supporting evidence.
