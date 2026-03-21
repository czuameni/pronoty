import os
import bcrypt

class AuthManager:
    def __init__(self):
        self.hash_file = "data/master.hash"

    def verify_or_set_password(self, password: str):
        password_bytes = password.encode()

        if not os.path.exists(self.hash_file):
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

            with open(self.hash_file, "wb") as f:
                f.write(hashed)

            return True

        with open(self.hash_file, "rb") as f:
            stored_hash = f.read()

        return bcrypt.checkpw(password_bytes, stored_hash)