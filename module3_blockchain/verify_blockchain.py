
import json
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEDGER_FILE = PROJECT_ROOT / "outputs" / "blockchain_ledger.json"


def calculate_hash(block):
    block_data = {
        key: value
        for key, value in block.items()
        if key != "hash"
    }

    encoded_data = json.dumps(
        block_data,
        sort_keys=True,
        separators=(",", ":")
    )
    return hashlib.sha256(encoded_data.encode("utf-8")).hexdigest()


def verify_blockchain(chain):
    if not isinstance(chain, list) or not chain:
        print("INVALID: Blockchain is empty or malformed.")
        return False

    for index, block in enumerate(chain):
        if not isinstance(block, dict):
            print(f"INVALID: Block {index} is malformed.")
            return False

        if block.get("index") != index:
            print(f"INVALID: Block index mismatch at block {index}.")
            return False

        if block.get("hash") != calculate_hash(block):
            print(f"INVALID: Block {index} data was modified.")
            return False

        if index == 0:
            if block.get("previous_hash") != "0":
                print("INVALID: Genesis block is incorrect.")
                return False
        else:
            if block.get("previous_hash") != chain[index - 1].get("hash"):
                print(f"INVALID: Previous hash mismatch at block {index}.")
                return False

    print("VALID: All blocks and hash links are correct.")
    return True


def main():
    print("===== BLOCKCHAIN VERIFICATION =====")

    if not LEDGER_FILE.exists():
        print("ERROR: Ledger not found. Run blockchain.py first.")
        return

    try:
        with LEDGER_FILE.open("r", encoding="utf-8") as file:
            chain = json.load(file)
    except (OSError, json.JSONDecodeError):
        print("ERROR: Could not read the ledger.")
        return

    verify_blockchain(chain)


if __name__ == "__main__":
    main()
