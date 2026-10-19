"""Klucz VAPID do powiadomień push (US-086). Uruchom raz:  python scripts/generate_vapid_key.py

Wypisuje VAPID_PRIVATE_KEY do wpisania w zmiennych środowiskowych (Coolify → Environment Variables) i klucz
publiczny do wglądu. Klucz prywatny to sekret: nie wklejaj go do repozytorium ani na czat. Zmiana klucza
unieważnia wszystkie subskrypcje — użytkownicy muszą ponownie włączyć push w ustawieniach."""
import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


key = ec.generate_private_key(ec.SECP256R1())
private = key.private_numbers().private_value.to_bytes(32, "big")
public = key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
print(f"VAPID_PRIVATE_KEY={b64(private)}")
print(f"# klucz publiczny (serwer liczy go sam): {b64(public)}")
