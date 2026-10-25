"""Run Module 1. Default source is the real MIT-BIH Arrhythmia Database."""
import argparse, json
from module1_acquisition.config import Config
from module1_acquisition.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Module 1: MIT-BIH ECG acquisition and preprocessing")
    parser.add_argument("--source", choices=["mitbih", "synthetic"], default="mitbih",
                        help="Use real MIT-BIH ECG (default) or synthetic demo ECG")
    parser.add_argument("--record", default="100", help="MIT-BIH record number, e.g. 100")
    parser.add_argument("--data-dir", default=None, help="Optional local folder containing MIT-BIH record files")
    parser.add_argument("--duration", type=int, default=120, help="Duration in seconds to process")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    args = parser.parse_args()
    cfg = Config(source=args.source, record=args.record, data_dir=args.data_dir,
                 duration_seconds=args.duration, output_dir=args.output_dir)
    summary = run_pipeline(cfg)
    print("\nModule 1 completed successfully.")
    print("Source:", summary["source"]["source"])
    print("Record:", summary["source"].get("record", "n/a"))
    print("Windows:", summary["window_shape"],
          f"(normal={summary['normal_windows']}, abnormal={summary['abnormal_windows']})")
    print(f"Normalized range: [{summary['normalized_min']:.3f}, {summary['normalized_max']:.3f}]")
    print("Outputs saved in:", args.output_dir)
    print("Important: HR, SpO2, BP, and temperature are simulated; only ECG/annotations are from MIT-BIH when --source mitbih is used.")
    print(json.dumps(summary["source"], indent=2))

if __name__ == "__main__":
    main()
