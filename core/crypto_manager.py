from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64, os


class CryptoManager:
    def __init__(self, password: str):
        self.salt_file = "data/crypto_salt.bin"
        self.salt = self._get_or_create_salt()

        self.key = self._derive_key(password, self.salt)
        self.fernet = Fernet(self.key)

    def _get_or_create_salt(self):
        if not os.path.exists(self.salt_file):
            salt = os.urandom(16)
            with open(self.salt_file, "wb") as f:
                f.write(salt)
        else:
            with open(self.salt_file, "rb") as f:
                salt = f.read()
        return salt

    def _derive_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())

    def decrypt(self, token: bytes) -> str:
        return self.fernet.decrypt(token).decode()