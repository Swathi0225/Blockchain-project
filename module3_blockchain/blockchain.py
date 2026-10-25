
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
ENCRYPTED_FILE = OUTPUT_DIR / "encrypted_features.jsonl"
LEDGER_FILE = OUTPUT_DIR / "blockchain_ledger.json"


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def calculate_hash(self, block):
        block_data = json.dumps(
            block,
            sort_keys=True,
            separators=(",", ":")
        )
        return hashlib.sha256(block_data.encode("utf-8")).hexdigest()

    def create_genesis_block(self):
        block = {
            "index": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "patient_id": "SYSTEM",
            "action": "GENESIS",
            "user": "SYSTEM",
            "previous_hash": "0"
        }
        block["hash"] = self.calculate_hash(block)
        self.chain.append(block)

    def add_block(self, patient_id, action, user):
        previous_block = self.chain[-1]

        block = {
            "index": len(self.chain),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "patient_id": patient_id,
            "action": action,
            "user": user,
            "previous_hash": previous_block["hash"]
        }

        block["hash"] = self.calculate_hash(block)
        self.chain.append(block)
        return block

    def verify_chain(self):
        for i, block in enumerate(self.chain):
            stored_hash = block.get("hash")
            block_data = {
                key: value
                for key, value in block.items()
                if key != "hash"
            }

            if stored_hash != self.calculate_hash(block_data):
                return False

            if i > 0:
                if block["previous_hash"] != self.chain[i - 1]["hash"]:
                    return False

        return True

    def save_chain(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with LEDGER_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.chain, file, indent=4)

    def load_chain(self):
        if not LEDGER_FILE.exists():
            return False

        try:
            with LEDGER_FILE.open("r", encoding="utf-8") as file:
                loaded_chain = json.load(file)

            if not isinstance(loaded_chain, list) or not loaded_chain:
                return False

            self.chain = loaded_chain
            return True
        except (OSError, json.JSONDecodeError):
            return False


def main():
    print("===== MODULE 3: BLOCKCHAIN ACCESS CONTROL =====")

    if not ENCRYPTED_FILE.exists():
        print("ERROR: Encrypted health data not found.")
        print("Complete Module 2 encryption first.")
        return

    # Confirm that encrypted data contains at least one record.
    with ENCRYPTED_FILE.open("r", encoding="utf-8") as file:
        has_data = any(line.strip() for line in file)

    if not has_data:
        print("ERROR: Encrypted health data file is empty.")
        return

    blockchain = Blockchain()
    blockchain.load_chain()

    # Demo access policy. Website login and database roles
    # will be integrated in a later stage.
    authorized_users = {"doctor01", "admin"}

    user = input("Enter username (doctor01/admin/guest): ").strip()
    patient_id = input("Enter patient ID (PATIENT-001): ").strip()

    if not patient_id:
        print("ERROR: Patient ID cannot be empty.")
        return

    if user in authorized_users:
        print("ACCESS GRANTED")
        blockchain.add_block(
            patient_id,
            "AUTHORIZED_HEALTH_DATA_ACCESS",
            user
        )
    else:
        print("ACCESS DENIED")
        blockchain.add_block(
            patient_id,
            "UNAUTHORIZED_ACCESS_ATTEMPT",
            user if user else "UNKNOWN"
        )

    blockchain.save_chain()

    print("Blockchain ledger saved:", LEDGER_FILE)
    print("Total blocks:", len(blockchain.chain))
    print("Blockchain integrity:", 
          "VALID" if blockchain.verify_chain() else "INVALID")


if __name__ == "__main__":
    main()
