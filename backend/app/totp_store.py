"""Sekret TOTP w bazie jest szyfrowany (ASVS 2.8.2, US-092): `crypto.encrypt` (Fernet,
DATA_ENCRYPTION_KEY). Wyciek kopii bazy nie zdradza wtedy kodów 2FA. Migracja totpenc001
zaszyfrowała istniejące sekrety; jawny wpis (np. z kopii sprzed migracji) dalej działa i jest
szyfrowany przy najbliższym udanym logowaniu."""
import logging

from cryptography.fernet import InvalidToken

from . import crypto
from .models import User

logger = logging.getLogger(__name__)


def seal(secret: str) -> str:
    return crypto.encrypt(secret)


def secret_of(user: User) -> str | None:
    """Jawny sekret do sprawdzenia kodu; None, gdy nie da się odszyfrować (zmieniony klucz)."""
    if not user.totp_secret:
        return None
    try:
        return crypto.decrypt(user.totp_secret)
    except InvalidToken:
        logger.error("Sekretu 2FA konta %s nie da się odszyfrować — sprawdź DATA_ENCRYPTION_KEY", user.id)
        return None


def reseal_if_plain(user: User, secret: str) -> None:
    if user.totp_secret and not crypto.is_encrypted(user.totp_secret):
        user.totp_secret = seal(secret)
