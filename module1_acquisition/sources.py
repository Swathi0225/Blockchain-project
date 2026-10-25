"""ECG sources: MIT-BIH Arrhythmia Database or optional synthetic demo data.

ECG and beat annotations can come from MIT-BIH (PhysioNet). Auxiliary vitals
(HR, SpO2, systolic/diastolic BP, temperature) are simulated and time-aligned;
they are not supplied by MIT-BIH.
"""
import os
import numpy as np
from .config import Config

ABNORMAL_SYMBOLS = {"V", "A", "L", "R", "a", "J", "S", "F", "e", "j", "E"}

def load_mitbih(cfg: Config):
    """Load a record and its .atr beat annotations with WFDB.

    Online mode uses PhysioNet's mitdb directory. Offline mode expects record
    files such as 100.dat, 100.hea, and 100.atr in cfg.data_dir.
    """
    try:
        import wfdb
    except ImportError as exc:
        raise RuntimeError("wfdb is not installed. Run: python -m pip install wfdb") from exc

    n = int(cfg.duration_seconds * cfg.fs)
    if cfg.data_dir:
        path, kwargs = os.path.join(cfg.data_dir, cfg.record), {}
    else:
        path, kwargs = cfg.record, {"pn_dir": "mitdb"}

    rec = wfdb.rdrecord(path, sampto=n, channels=[0], **kwargs)
    ann = wfdb.rdann(path, "atr", sampto=n, **kwargs)
    ecg = rec.p_signal[:, 0].astype(float)
    if int(round(rec.fs)) != cfg.fs:
        raise ValueError(f"Record sampled at {rec.fs} Hz but configured fs is {cfg.fs} Hz.")

    mask = np.zeros(len(ecg), dtype=bool)
    half = max(1, cfg.fs // 2)
    abnormal_beats = 0
    for sample, symbol in zip(ann.sample, ann.symbol):
        if symbol in ABNORMAL_SYMBOLS:
            start, end = max(0, int(sample) - half), min(len(mask), int(sample) + half)
            mask[start:end] = True
            abnormal_beats += 1

    meta = {
        "source": "MIT-BIH Arrhythmia Database (PhysioNet)",
        "record": cfg.record,
        "lead": rec.sig_name[0] if rec.sig_name else "unknown",
        "abnormal_beats": abnormal_beats,
        "n_annotations": int(len(ann.sample)),
        "sampling_frequency_hz": float(rec.fs),
        "note": "ECG and annotations are from MIT-BIH; auxiliary vitals are simulated."
    }
    return ecg, mask, meta

def _episodes(cfg: Config, rng):
    lo, hi, length = cfg.calibration_seconds + 5, cfg.duration_seconds - 8, 6.0
    if hi <= lo:
        return []
    count = max(1, int((hi - lo) // 25))
    slots = np.linspace(lo, hi, count + 1)
    episodes = []
    for a, b in zip(slots[:-1], slots[1:]):
        upper = max(a, b - length)
        start = rng.uniform(a, upper) if upper > a else a
        episodes.append((start, start + length))
    return episodes

def _beat(fs, pvc):
    t = np.arange(-0.35, 0.55, 1.0 / fs)
    if pvc:
        components = [(0.0, 0.045, 1.5), (0.20, 0.08, -0.5)]
    else:
        components = [(-0.20, 0.025, 0.12), (-0.04, 0.010, -0.15),
                      (0.0, 0.012, 1.0), (0.04, 0.012, -0.25), (0.25, 0.05, 0.30)]
    return t, sum(a * np.exp(-0.5 * ((t - mu) / sigma) ** 2) for mu, sigma, a in components)

def synthetic_ecg(cfg: Config, rng):
    fs, n = cfg.fs, int(cfg.duration_seconds * cfg.fs)
    episodes = _episodes(cfg, rng)
    def in_episode(sec):
        return any(a <= sec <= b for a, b in episodes)
    ecg = np.zeros(n, dtype=float)
    mask = np.zeros(n, dtype=bool)
    for a, b in episodes:
        mask[max(0, int(a * fs)):min(n, int(b * fs))] = True
    r, abnormal_beats = 0.5, 0
    while r < cfg.duration_seconds - 0.6:
        rr = 60.0 / 72.0 * (1 + 0.03 * rng.standard_normal())
        nxt = r + rr
        pvc = in_episode(nxt) and rng.random() < 0.5
        if pvc:
            nxt, abnormal_beats = r + 0.65 * rr, abnormal_beats + 1
        t, y = _beat(fs, pvc)
        i0 = int(round((nxt + t[0]) * fs))
        valid_start, valid_end = max(0, -i0), min(len(y), n - i0)
        if valid_end > valid_start:
            ecg[i0 + valid_start:i0 + valid_end] += y[valid_start:valid_end]
        r = nxt
    tt = np.arange(n) / fs
    ecg += 0.05 * np.sin(2 * np.pi * 0.3 * tt) + 0.02 * rng.standard_normal(n)
    for _ in range(3):
        gap = int(rng.integers(5, 20))
        if n > 2 * fs:
            start = int(rng.integers(fs, n - fs))
            ecg[start:min(n, start + gap)] = np.nan
    meta = {"source": "Synthetic ECG (demo fallback)", "record": "synthetic", "lead": "synthetic-II",
            "abnormal_beats": abnormal_beats, "episodes": [(round(a, 1), round(b, 1)) for a, b in episodes]}
    return ecg, mask, meta

def simulate_vitals(mask: np.ndarray, cfg: Config, rng):
    """Generate simulated 1 Hz vitals aligned with ECG abnormality mask."""
    n_sec = len(mask) // cfg.fs
    sec_mask = mask[:n_sec * cfg.fs].reshape(n_sec, cfg.fs).any(axis=1)
    t = np.arange(n_sec)
    effect = np.convolve(sec_mask.astype(float), np.ones(3) / 3, mode="same")
    hr = 72 + 4 * np.sin(2 * np.pi * t / 60) + rng.normal(0, 1.0, n_sec) + 35 * effect
    spo2 = np.clip(97.5 + rng.normal(0, 0.4, n_sec) - 6 * effect, 70, 100)
    sbp = 120 + 3 * np.sin(2 * np.pi * t / 90) + rng.normal(0, 1.5, n_sec) + 25 * effect
    dbp = 80 + 2 * np.sin(2 * np.pi * t / 90) + rng.normal(0, 1.0, n_sec) + 10 * effect
    temp = 36.8 + 0.05 * np.sin(2 * np.pi * t / 120) + rng.normal(0, 0.03, n_sec) + 0.4 * effect
    vitals = np.column_stack([hr, spo2, sbp, dbp, temp])
    drop = rng.random(vitals.shape) < cfg.dropout_prob
    if len(vitals):
        drop[0, :] = False
    vitals[drop] = np.nan
    return vitals

def load_signals(cfg: Config):
    rng = np.random.default_rng(cfg.seed)
    if cfg.source == "mitbih":
        ecg, mask, meta = load_mitbih(cfg)
    elif cfg.source == "synthetic":
        ecg, mask, meta = synthetic_ecg(cfg, rng)
    else:
        raise ValueError("source must be 'synthetic' or 'mitbih'")
    seconds = len(ecg) // cfg.fs
    ecg, mask = ecg[:seconds * cfg.fs], mask[:seconds * cfg.fs]
    vitals = simulate_vitals(mask, cfg, rng)
    return ecg, vitals, mask, meta
