
import csv
import json
import math
from pathlib import Path

from module2_encryption.key_manager import load_keys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "outputs" / "normalized_features.csv"
OUTPUT_FILE = PROJECT_ROOT / "outputs" / "encrypted_features.jsonl"

HEALTH_FEATURES = ["HR", "SpO2", "SBP", "DBP", "Temp", "ECG"]


def main():
    if not INPUT_FILE.exists():
        print("ERROR: normalized_features.csv not found!")
        return

    try:
        public_key, _ = load_keys()
    except FileNotFoundError:
        print("ERROR: Saved keys not found.")
        return

    count = 0

    with INPUT_FILE.open("r", newline="", encoding="utf-8") as csvfile, \
         OUTPUT_FILE.open("w", encoding="utf-8") as outfile:

        reader = csv.DictReader(csvfile)

        missing = set(HEALTH_FEATURES) - set(reader.fieldnames or [])
        if missing:
            print("ERROR: Missing columns:", sorted(missing))
            return

        for row in reader:
            encrypted_row = {}

            for feature in HEALTH_FEATURES:
                try:
                    value = float(row[feature])

                    if math.isfinite(value):
                        encrypted = public_key.encrypt(value)
                        encrypted_row[feature] = {
                            "ciphertext": str(encrypted.ciphertext()),
                            "exponent": encrypted.exponent
                        }

                except (ValueError, TypeError):
                    continue

            outfile.write(json.dumps(encrypted_row) + "\n")
            count += 1

            if count >= 100:
                break

    print("Encryption completed using saved public key.")
    print("Rows processed:", count)
    print("Encrypted features:", ", ".join(HEALTH_FEATURES))
    print("Ciphertext and exponent saved.")
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
