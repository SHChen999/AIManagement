import base64
import hashlib
from cryptography.fernet import Fernet
from core.config import get_settings


def _get_fernet() -> Fernet:
    key = get_settings().encryption_key.encode()
    hashed = hashlib.sha256(key).digest()
    fernet_key = base64.urlsafe_b64encode(hashed)
    return Fernet(fernet_key)


def encrypt(plaintext: str) -> str:
    if not plaintext:
        return plaintext
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    if not ciphertext:
        return ciphertext
    return _get_fernet().decrypt(ciphertext.encode()).decode()
