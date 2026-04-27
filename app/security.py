import base64, hashlib, hmac, secrets
from datetime import datetime, timezone

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 720000


def make_token() -> str:
    return secrets.token_hex(20)


def django_pbkdf2_sha256(password: str, salt: str | None = None, iterations: int = ITERATIONS) -> str:
    salt = salt or secrets.token_urlsafe(12)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    hash_b64 = base64.b64encode(dk).decode().strip()
    return f"{ALGORITHM}${iterations}${salt}${hash_b64}"


def verify_django_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, hash_b64 = encoded.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        candidate = django_pbkdf2_sha256(password, salt, int(iterations))
        return hmac.compare_digest(candidate, encoded)
    except Exception:
        return False
