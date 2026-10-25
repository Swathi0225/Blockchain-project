
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENCRYPTED_FILE = PROJECT_ROOT / "outputs" / "encrypted_features.jsonl"

# Use the existing blockchain implementation.
from blockchain import Blockchain


AUTHORIZED_USERS = {"doctor01", "admin"}
PATIENT_ID = "PATIENT-001"


def main():
    print("===== MODULE 3: SECURE HEALTH DATA ACCESS =====")

    if not ENCRYPTED_FILE.exists():
        print("ERROR: Encrypted data file not found.")
        print("Run Module 2 encryption first.")
        return

    # Read encrypted records without decrypting health values.
    encrypted_records = []

    try:
        with ENCRYPTED_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    encrypted_records.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as error:
        print("ERROR: Could not read encrypted data:", error)
        return

    if not encrypted_records:
        print("ERROR: No encrypted records found.")
        return

    user = input("Enter username (doctor01/admin/guest): ").strip()
    patient_id = input("Enter patient ID (PATIENT-001): ").strip()

    if not user or not patient_id:
        print("ERROR: Username and patient ID are required.")
        return

    blockchain = Blockchain()
    blockchain.load_chain()

    if user in AUTHORIZED_USERS:
        blockchain.add_block(
            patient_id,
            "AUTHORIZED_ENCRYPTED_DATA_ACCESS",
            user
        )
        print("ACCESS GRANTED")
        print("Encrypted records available:", len(encrypted_records))
        print("Health values remain encrypted.")
    else:
        blockchain.add_block(
            patient_id,
            "UNAUTHORIZED_ACCESS_ATTEMPT",
            user
        )
        print("ACCESS DENIED")
        print("Encrypted records were not provided to the user.")

    blockchain.save_chain()

    print("Access attempt saved to blockchain ledger.")
    print(
        "Ledger integrity:",
        "VALID" if blockchain.verify_chain() else "INVALID"
    )


if __name__ == "__main__":
    main()
