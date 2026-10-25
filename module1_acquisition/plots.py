"""Create a quick-look figure for Module 1 outputs."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def create_overview(raw_ecg, normalized, mask, fs, output_path):
    seconds = np.arange(len(raw_ecg)) / fs
    n = min(len(raw_ecg), fs * 20)
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), constrained_layout=True)
    axes[0].plot(seconds[:n], raw_ecg[:n], linewidth=0.7)
    axes[0].set_title("ECG signal (first 20 seconds or less)")
    axes[0].set_xlabel("Time (s)"); axes[0].set_ylabel("ECG (mV)")
    axes[1].plot(seconds[:n], normalized[:n, 0], label="HR", linewidth=0.8)
    axes[1].plot(seconds[:n], normalized[:n, 1], label="SpO2", linewidth=0.8)
    axes[1].set_title("Example normalized vital-sign features"); axes[1].legend(loc="upper right")
    axes[1].set_xlabel("Time (s)"); axes[1].set_ylabel("Normalized value")
    axes[2].plot(seconds[:n], mask[:n].astype(int), linewidth=0.8)
    axes[2].set_title("Abnormal-episode mask from annotations/source")
    axes[2].set_xlabel("Time (s)"); axes[2].set_ylabel("Abnormal")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
