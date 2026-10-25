"""Missing-value handling, feature alignment, normalization, and windowing."""
import numpy as np
import pandas as pd
from .config import Config, FEATURE_NAMES

def interpolate_missing(values):
    """Linear interpolation over NaN values; also handles all-NaN columns safely."""
    arr = np.asarray(values, dtype=float).copy()
    if arr.ndim == 1:
        s = pd.Series(arr).interpolate(limit_direction="both")
        return s.fillna(0.0).to_numpy(dtype=float)
    out = np.empty_like(arr, dtype=float)
    for col in range(arr.shape[1]):
        s = pd.Series(arr[:, col]).interpolate(limit_direction="both")
        out[:, col] = s.fillna(0.0).to_numpy(dtype=float)
    return out

def build_composite_features(ecg, vitals_1hz, cfg: Config):
    """Align 1 Hz vitals to ECG samples and return [HR, SpO2, SBP, DBP, Temp, ECG]."""
    ecg = interpolate_missing(ecg)
    vitals = interpolate_missing(vitals_1hz)
    sample_seconds = np.arange(len(ecg)) / cfg.fs
    indices = np.minimum(sample_seconds.astype(int), max(0, len(vitals) - 1))
    aligned_vitals = vitals[indices]
    return np.column_stack([aligned_vitals, ecg])

def normalize_features(features, cfg: Config):
    """Min-max normalize each feature using the calibration portion, clipping to [0,1]."""
    features = np.asarray(features, dtype=float)
    calibration_n = min(max(1, cfg.calibration_samples), len(features))
    calibration = features[:calibration_n]
    mins = np.nanmin(calibration, axis=0)
    maxs = np.nanmax(calibration, axis=0)
    spans = maxs - mins
    spans[spans == 0] = 1.0
    normalized = (features - mins) / spans
    if cfg.clip:
        normalized = np.clip(normalized, 0.0, 1.0)
    return normalized, mins, maxs

def make_windows(features, mask, cfg: Config):
    window, stride = cfg.window_samples, cfg.stride_samples
    if len(features) < window:
        raise ValueError(f"Need at least {window} samples to create a window; got {len(features)}")
    starts = np.arange(0, len(features) - window + 1, stride, dtype=int)
    windows = np.stack([features[s:s + window] for s in starts])
    labels = np.array([bool(np.any(mask[s:s + window])) for s in starts], dtype=bool)
    return windows, labels, starts
