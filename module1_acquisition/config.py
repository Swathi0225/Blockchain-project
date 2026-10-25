"""Central configuration for Module 1."""
from dataclasses import dataclass
from typing import Optional

FEATURE_NAMES = ["HR", "SpO2", "SBP", "DBP", "Temp", "ECG"]
UNITS = {"HR": "bpm", "SpO2": "%", "SBP": "mmHg", "DBP": "mmHg", "Temp": "degC", "ECG": "mV"}

@dataclass
class Config:
    # Real MIT-BIH data is the default. Use source="synthetic" only for offline demos/tests.
    source: str = "mitbih"          # "mitbih" or "synthetic"
    record: str = "100"             # MIT-BIH record identifier
    data_dir: Optional[str] = None  # optional folder containing 100.dat, 100.hea, 100.atr
    duration_seconds: int = 120
    fs: int = 360
    window_seconds: int = 5
    stride_seconds: float = 2.5
    calibration_seconds: int = 60
    clip: bool = True
    dropout_prob: float = 0.02
    packet_hz: float = 1.0
    patient_id: str = "PATIENT-001"  # demo identifier; not a real patient identity
    device_id: str = "EDGE-GW-01"
    seed: int = 42
    output_dir: str = "outputs"

    @property
    def window_samples(self) -> int:
        return int(self.window_seconds * self.fs)

    @property
    def stride_samples(self) -> int:
        return int(self.stride_seconds * self.fs)

    @property
    def calibration_samples(self) -> int:
        return int(self.calibration_seconds * self.fs)
