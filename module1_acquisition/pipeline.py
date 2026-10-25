"""End-to-end Module 1 pipeline."""
import json, os
import numpy as np
import pandas as pd
from .config import Config, FEATURE_NAMES
from .sources import load_signals
from .preprocessing import build_composite_features, normalize_features, make_windows
from .plots import create_overview

def run_pipeline(cfg: Config):
    os.makedirs(cfg.output_dir, exist_ok=True)
    ecg, vitals, mask, meta = load_signals(cfg)
    # Save raw source data before interpolation/normalization.
    raw_vitals = np.repeat(vitals, cfg.fs, axis=0)[:len(ecg)]
    raw_df = pd.DataFrame(np.column_stack([raw_vitals, ecg]), columns=FEATURE_NAMES)
    raw_df.insert(0, "time_seconds", np.arange(len(ecg)) / cfg.fs)
    raw_df.to_csv(os.path.join(cfg.output_dir, "raw_signals.csv"), index=False)

    features = build_composite_features(ecg, vitals, cfg)
    normalized, mins, maxs = normalize_features(features, cfg)
    norm_df = pd.DataFrame(normalized, columns=FEATURE_NAMES)
    norm_df.insert(0, "time_seconds", np.arange(len(ecg)) / cfg.fs)
    norm_df.to_csv(os.path.join(cfg.output_dir, "normalized_features.csv"), index=False)

    windows, labels, starts = make_windows(normalized, mask, cfg)
    np.savez_compressed(os.path.join(cfg.output_dir, "windows.npz"), windows=windows, labels=labels, starts=starts)
    with open(os.path.join(cfg.output_dir, "calibration.json"), "w", encoding="utf-8") as f:
        json.dump({"feature_names": FEATURE_NAMES, "min": mins.tolist(), "max": maxs.tolist(),
                   "calibration_seconds": cfg.calibration_seconds}, f, indent=2)

    packet_path = os.path.join(cfg.output_dir, "feature_packets.jsonl")
    step = max(1, int(cfg.fs / cfg.packet_hz))
    with open(packet_path, "w", encoding="utf-8") as f:
        for idx in range(0, len(normalized), step):
            packet = {"patient_id": cfg.patient_id, "device_id": cfg.device_id,
                      "time_seconds": round(idx / cfg.fs, 3),
                      "features": {name: round(float(value), 6) for name, value in zip(FEATURE_NAMES, normalized[idx])},
                      "abnormal": bool(mask[idx])}
            f.write(json.dumps(packet) + "\n")

    create_overview(ecg, normalized, mask, cfg.fs, os.path.join(cfg.output_dir, "module1_overview.png"))
    summary = {
        "source": meta, "patient_id": cfg.patient_id, "device_id": cfg.device_id,
        "duration_seconds_processed": len(ecg) / cfg.fs,
        "sampling_frequency_hz": cfg.fs, "features": FEATURE_NAMES,
        "raw_samples": int(len(ecg)), "window_shape": list(windows.shape),
        "normal_windows": int(np.sum(~labels)), "abnormal_windows": int(np.sum(labels)),
        "normalized_min": float(np.min(normalized)), "normalized_max": float(np.max(normalized)),
        "vital_signs_source": "simulated (HR, SpO2, SBP, DBP, Temp)",
        "warning": "This is a research/demo pipeline, not a medical diagnostic system."
    }
    with open(os.path.join(cfg.output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary
