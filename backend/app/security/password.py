from pwdlib import PasswordHash

# Initialize password hasher using Argon2id (recommended modern standard)
_password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """
    Hashes a plaintext password using Argon2id.
    """
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against an Argon2 hashed password.
    Returns True if matches, False otherwise.
    """
    return _password_hash.verify(plain_password, hashed_password)
