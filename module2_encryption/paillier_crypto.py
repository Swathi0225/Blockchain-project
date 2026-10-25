
from phe import paillier


def generate_keys():
    """Generate Paillier public and private keys."""
    public_key, private_key = paillier.generate_paillier_keypair(
        n_length=2048
    )
    return public_key, private_key


def encrypt_value(public_key, value):
    """Encrypt one numerical value."""
    return public_key.encrypt(float(value))


def decrypt_value(private_key, encrypted_value):
    """Decrypt one encrypted value."""
    return private_key.decrypt(encrypted_value)


def main():
    public_key, private_key = generate_keys()

    original_value = 0.75
    encrypted_value = encrypt_value(public_key, original_value)
    decrypted_value = decrypt_value(private_key, encrypted_value)

    print("Original value:", original_value)
    print("Encrypted value: Encryption successful")
    print("Decrypted value:", decrypted_value)


if __name__ == "__main__":
    main()
