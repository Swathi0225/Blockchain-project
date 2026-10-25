
import csv
from pathlib import Path
from phe import paillier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "outputs" / "normalized_features.csv"


def main():
    with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        first_row = next(reader)

    # Select one numeric, non-empty value
    column = next(
        key for key, value in first_row.items()
        if value and value.lower() != "nan"
        and _is_number(value)
    )
    original_value = float(first_row[column])

    public_key, private_key = paillier.generate_paillier_keypair(
        n_length=2048
    )
    encrypted_value = public_key.encrypt(original_value)
    decrypted_value = private_key.decrypt(encrypted_value)

    print("Feature:", column)
    print("Original value:", original_value)
    print("Encrypted value: Encryption successful")
    print("Decrypted value:", decrypted_value)
    print("Verification:", "PASSED" if abs(
        original_value - decrypted_value
    ) < 1e-8 else "FAILED")


def _is_number(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


if __name__ == "__main__":
    main()
