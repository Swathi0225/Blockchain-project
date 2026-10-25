# Module 1 — Patient Health Data Acquisition and Normalization

This standalone project implements Module 1 of the secure healthcare monitoring project.
**The default source is the real MIT-BIH Arrhythmia Database (record 100) from PhysioNet.**

## Data-source transparency

- With the default command, ECG samples and beat annotations are loaded from MIT-BIH through `wfdb` and PhysioNet. Internet access is required the first time unless the files are downloaded locally.
- HR, SpO2, systolic BP, diastolic BP, and temperature are **simulated** by this code and aligned to the ECG timeline. MIT-BIH is an ECG arrhythmia database; it does not provide those five vital-sign streams in this project.
- The `PATIENT-001` value is a demo/configuration identifier, not a real patient's identity or a patient record lookup.
- Synthetic ECG is available only as an explicit fallback with `--source synthetic`.
- This is a research/demo pipeline, not a medical diagnostic system.

## 1. Install Python

Use Python 3.10+ if possible. Open PowerShell in this folder.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the commands below without activating the environment, using your installed Python.

## 2. Run with real MIT-BIH data (default)

```powershell
python run_module1.py
```

This loads record `100` from PhysioNet's `mitdb` database and processes the first 120 seconds. Internet access is needed in online mode.

You can select a different duration or record:

```powershell
python run_module1.py --record 100 --duration 120
```

### Offline/local record files

Download the matching record files from the MIT-BIH Arrhythmia Database (at minimum `100.dat`, `100.hea`, and `100.atr`) into a folder, for example `data/mitdb/`, then run:

```powershell
python run_module1.py --data-dir data/mitdb --record 100
```

The local folder should contain the files directly, not an extra nested folder.

## 3. Optional synthetic test data

Only use this when testing offline or demonstrating the fallback:

```powershell
python run_module1.py --source synthetic
```

The console output and `outputs/summary.json` report which source was used. Check this before presenting results to your guide.

## 4. Output files

- `outputs/raw_signals.csv` — source ECG and simulated vitals before normalization (missing values may appear).
- `outputs/normalized_features.csv` — interpolated and min-max normalized six-feature vector `[HR, SpO2, SBP, DBP, Temp, ECG]`.
- `outputs/windows.npz` — overlapping 5-second feature windows, labels, and start indices.
- `outputs/feature_packets.jsonl` — per-second normalized feature packets with demo patient/device IDs.
- `outputs/calibration.json` — min/max calibration values and feature names.
- `outputs/summary.json` — selected data source, record metadata, counts, and window statistics.
- `outputs/module1_overview.png` — overview plot.

## 5. Tests

```powershell
python -m pytest tests -v
```

## Processing overview

1. Acquire ECG and annotations from MIT-BIH (or explicitly selected synthetic fallback).
2. Create time-aligned simulated auxiliary vital signs.
3. Interpolate missing samples.
4. Build the composite feature vector `[HR, SpO2, SBP, DBP, Temp, ECG]`.
5. Normalize using the calibration interval and clip values to `[0, 1]`.
6. Create 5-second windows with 50% overlap and mark windows that overlap abnormal annotated episodes.
7. Save CSV, NPZ, JSON/JSONL, and figure outputs.
