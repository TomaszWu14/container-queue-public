"""Kody zapasowe 2FA (US-088, ASVS 2.6.2/2.6.3) — wydzielone z security.py."""
import hashlib
import hmac
import secrets

# Kody zapasowe 2FA (US-088, ASVS 2.6.2/2.6.3): 12 znaków z alfabetu bez mylących znaków (60 bitów),
# w bazie „s1$<sól>$<scrypt>” — sól na kod i wolny hash, więc wyciek bazy nie pozwala ich szybko odgadnąć.
# Stare kody (SHA-256 bez soli, 64 znaki hex) dalej działają do ponownego wygenerowania.
_BACKUP_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_SCRYPT = {"n": 2**14, "r": 8, "p": 1, "dklen": 32}


def _normalize_backup(raw: str) -> str:
    return "".join(ch for ch in raw.upper() if ch.isalnum())


def _legacy_backup_hash(raw: str) -> str:
    return hashlib.sha256(raw.strip().replace("-", "").lower().encode("utf-8")).hexdigest()


def hash_backup_code(raw: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(_normalize_backup(raw).encode(), salt=salt, **_SCRYPT)
    return f"s1${salt.hex()}${digest.hex()}"


def match_backup_code(raw: str, stored: list[str]) -> str | None:
    """Zwraca zapisany hash pasujący do kodu (do usunięcia — kod jednorazowy) albo None."""
    for entry in stored:
        if entry.startswith("s1$"):
            _, salt_hex, _digest = entry.split("$", 2)
            ok = hmac.compare_digest(hash_backup_code(raw, bytes.fromhex(salt_hex)), entry)
        else:
            ok = hmac.compare_digest(_legacy_backup_hash(raw), entry)
        if ok:
            return entry
    return None


def generate_backup_codes(n: int = 10) -> list[str]:
    """10 kodów zapasowych XXXX-XXXX-XXXX (pokazywane raz; w bazie tylko solone hashe scrypt)."""
    def one() -> str:
        raw = "".join(secrets.choice(_BACKUP_ALPHABET) for _ in range(12))
        return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"
    return [one() for _ in range(n)]
