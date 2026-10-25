
import json
from pathlib import Path
from phe import paillier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEY_DIR = PROJECT_ROOT / "secure_keys"
PUBLIC_KEY_FILE = KEY_DIR / "public_key.json"
PRIVATE_KEY_FILE = KEY_DIR / "private_key.json"


def save_keys():
    """Generate and save a Paillier key pair."""
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    public_key, private_key = paillier.generate_paillier_keypair(
        n_length=2048
    )

    public_data = {
        "n": str(public_key.n)
    }

    private_data = {
        "p": str(private_key.p),
        "q": str(private_key.q)
    }

    PUBLIC_KEY_FILE.write_text(
        json.dumps(public_data, indent=2),
        encoding="utf-8"
    )
    PRIVATE_KEY_FILE.write_text(
        json.dumps(private_data, indent=2),
        encoding="utf-8"
    )

    print("Paillier key pair generated and saved.")
    print("Public key:", PUBLIC_KEY_FILE)
    print("Private key:", PRIVATE_KEY_FILE)
    print("IMPORTANT: Never upload private_key.json to GitHub.")


def load_keys():
    """Load the saved Paillier key pair."""
    public_data = json.loads(
        PUBLIC_KEY_FILE.read_text(encoding="utf-8")
    )
    private_data = json.loads(
        PRIVATE_KEY_FILE.read_text(encoding="utf-8")
    )

    public_key = paillier.PaillierPublicKey(
        n=int(public_data["n"])
    )

    private_key = paillier.PaillierPrivateKey(
        public_key,
        int(private_data["p"]),
        int(private_data["q"])
    )

    return public_key, private_key


if __name__ == "__main__":
    save_keys()
