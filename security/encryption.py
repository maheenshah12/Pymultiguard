"""
Encryption module for securing sensitive data.
Uses AES-256 encryption with Fernet (symmetric encryption).
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json


class EncryptionManager:
    """Manages encryption/decryption of sensitive data."""

    def __init__(self, master_password: str = None):
        """Initialize encryption with master password or generate new key."""
        if master_password:
            self.key = self._derive_key_from_password(master_password)
        else:
            # Use machine-specific key stored in .encryption_key file
            key_file = ".encryption_key"
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    self.key = f.read()
            else:
                self.key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(self.key)
                print(f"[Security] Generated new encryption key: {key_file}")

        self.cipher = Fernet(self.key)

    def _derive_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = b'pymultiguard_salt_v1'  # Fixed salt for consistency

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """Encrypt string data and return base64 encoded result."""
        if not data:
            return ""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data and return original string."""
        if not encrypted_data:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def encrypt_dict(self, data: dict) -> str:
        """Encrypt dictionary as JSON string."""
        json_str = json.dumps(data)
        return self.encrypt(json_str)

    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Decrypt and parse JSON dictionary."""
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)

    def encrypt_file(self, input_file: str, output_file: str = None):
        """Encrypt entire file."""
        if output_file is None:
            output_file = input_file + ".encrypted"

        with open(input_file, "rb") as f:
            data = f.read()

        encrypted = self.cipher.encrypt(data)

        with open(output_file, "wb") as f:
            f.write(encrypted)

        return output_file

    def decrypt_file(self, input_file: str, output_file: str = None):
        """Decrypt entire file."""
        if output_file is None:
            output_file = input_file.replace(".encrypted", "")

        with open(input_file, "rb") as f:
            encrypted_data = f.read()

        decrypted = self.cipher.decrypt(encrypted_data)

        with open(output_file, "wb") as f:
            f.write(decrypted)

        return output_file


def encrypt_env_file(env_file: str = ".env", output_file: str = ".env.encrypted"):
    """Encrypt .env file for secure storage."""
    manager = EncryptionManager()

    # Read .env file
    env_data = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_data[key.strip()] = value.strip()

    # Encrypt and save
    encrypted = manager.encrypt_dict(env_data)
    with open(output_file, "w") as f:
        f.write(encrypted)

    print(f"[Security] Encrypted {len(env_data)} environment variables")
    print(f"[Security] Saved to: {output_file}")
    return output_file


def decrypt_env_file(encrypted_file: str = ".env.encrypted") -> dict:
    """Decrypt .env file and return as dictionary."""
    manager = EncryptionManager()

    with open(encrypted_file, "r") as f:
        encrypted_data = f.read()

    env_data = manager.decrypt_dict(encrypted_data)
    print(f"[Security] Decrypted {len(env_data)} environment variables")
    return env_data


if __name__ == "__main__":
    # Test encryption
    manager = EncryptionManager()

    # Test string encryption
    original = "sensitive_password_123"
    encrypted = manager.encrypt(original)
    decrypted = manager.decrypt(encrypted)

    print(f"Original: {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")
