import numpy as np
from module1_acquisition.config import Config
from module1_acquisition.preprocessing import interpolate_missing, normalize_features, make_windows
from module1_acquisition.sources import synthetic_ecg, simulate_vitals

def test_interpolation_removes_nan():
    x = interpolate_missing([1.0, np.nan, 3.0])
    assert np.isfinite(x).all()
    assert x[1] == 2.0

def test_normalization_clips_to_unit_interval():
    cfg = Config(source="synthetic", duration_seconds=10, calibration_seconds=5)
    x = np.array([[0., 2.], [1., 4.], [3., 8.]])
    normalized, _, _ = normalize_features(x, cfg)
    assert normalized.min() >= 0.0 and normalized.max() <= 1.0

def test_window_shape_and_labels():
    cfg = Config(source="synthetic", duration_seconds=10, calibration_seconds=2)
    x = np.zeros((cfg.fs * 10, 6))
    mask = np.zeros(len(x), dtype=bool)
    mask[100:200] = True
    windows, labels, starts = make_windows(x, mask, cfg)
    assert windows.shape[1:] == (cfg.window_samples, 6)
    assert len(labels) == len(starts)
    assert labels.any()

def test_synthetic_source_and_vitals():
    cfg = Config(source="synthetic", duration_seconds=30, calibration_seconds=5)
    rng = np.random.default_rng(cfg.seed)
    ecg, mask, meta = synthetic_ecg(cfg, rng)
    vitals = simulate_vitals(mask, cfg, rng)
    assert len(ecg) == cfg.duration_seconds * cfg.fs
    assert vitals.shape == (cfg.duration_seconds, 5)
    assert meta["source"].startswith("Synthetic")
