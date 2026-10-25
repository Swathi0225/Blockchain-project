
import csv
import json
import math
from pathlib import Path

from phe import paillier
from module2_encryption.key_manager import load_keys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "outputs" / "normalized_features.csv"
ENCRYPTED_FILE = PROJECT_ROOT / "outputs" / "encrypted_features.jsonl"

HEALTH_FEATURES = ["HR", "SpO2", "SBP", "DBP", "Temp", "ECG"]


def main():
    public_key, private_key = load_keys()

    with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
        original_row = next(csv.DictReader(file))

    with ENCRYPTED_FILE.open("r", encoding="utf-8") as file:
        encrypted_row = json.loads(file.readline())

    all_passed = True
    print("Saved ciphertext decryption verification:")

    for feature in HEALTH_FEATURES:
        if feature not in encrypted_row:
            print(f"{feature}: SKIPPED")
            all_passed = False
            continue

        item = encrypted_row[feature]
        encrypted_number = paillier.EncryptedNumber(
            public_key,
            int(item["ciphertext"]),
            int(item["exponent"])
        )

        original_value = float(original_row[feature])
        decrypted_value = private_key.decrypt(encrypted_number)

        passed = math.isclose(
            original_value, decrypted_value,
            rel_tol=1e-8, abs_tol=1e-8
        )
        all_passed = all_passed and passed

        print(
            f"{feature}: original={original_value:.8f}, "
            f"decrypted={decrypted_value:.8f}, "
            f"{'PASSED' if passed else 'FAILED'}"
        )

    print("Overall result:", "PASSED" if all_passed else "FAILED")


if __name__ == "__main__":
    main()
