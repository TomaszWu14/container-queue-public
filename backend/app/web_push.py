"""Powiadomienia push na telefon i w przeglądarce (czwarta lista PO, pkt 2, US-086).

Tylko najpilniejsze rodzaje alertów (URGENT_KINDS, założenie Z-045) i tylko u osób, które same włączyły push
na danym urządzeniu (Ustawienia → Powiadomienia). Push idzie obok dzwonka, nie zamiast: gdy dzwonek dla roli
jest wyłączony w matrycy, push też nie wychodzi.

Standard Web Push (RFC 8030/8291/8292): treść szyfrowana kluczem przeglądarki (aes128gcm, biblioteka http-ece),
serwer przedstawia się kluczem VAPID (JWT ES256 przez PyJWT). Bez zmiennej VAPID_PRIVATE_KEY funkcja jest
wyłączona, a przełącznik w ustawieniach mówi to wprost.

[SEC] Adres subskrypcji podaje przeglądarka, a serwer wysyła na niego żądanie — dlatego tylko https i tylko
hosty znanych usług push (PUSH_HOSTS; bez tego byłby to SSRF). W treści wyłącznie tytuł alertu i link do
aplikacji (bez opisu). Zapis bez migracji: ustawienie `push_subs:{user_id}`, najwyżej MAX_SUBS urządzeń."""
from __future__ import annotations

import base64
import json
import logging
import time
from collections.abc import Iterable
from urllib.parse import urlsplit

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import app_settings
from .config import settings
from .models import AppSetting

logger = logging.getLogger(__name__)

PREFIX = "push_subs:"
MAX_SUBS = 5
TTL_SECONDS = 12 * 3600
URGENT_KINDS = frozenset({"mention", "demurrage", "eta_overdue", "gate", "pallet_urgent", "customs-delay",
                          "freight_approval", "vessel_stuck"})
PUSH_HOSTS = ("fcm.googleapis.com", "updates.push.services.mozilla.com", "push.services.mozilla.com",
              "push.apple.com", "notify.windows.com")


def _b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _private_key() -> ec.EllipticCurvePrivateKey | None:
    raw = (settings.vapid_private_key or "").strip()
    if not raw:
        return None
    try:
        return ec.derive_private_key(int.from_bytes(_b64d(raw), "big"), ec.SECP256R1())
    except ValueError:
        logger.error("VAPID_PRIVATE_KEY ma zły format — push wyłączony")
        return None


def public_key() -> str | None:
    """Klucz publiczny VAPID (applicationServerKey dla przeglądarki) albo None, gdy push wyłączony."""
    key = _private_key()
    if key is None:
        return None
    return _b64e(key.public_key().public_bytes(serialization.Encoding.X962,
                                               serialization.PublicFormat.UncompressedPoint))


def allowed_endpoint(endpoint: str) -> bool:
    parts = urlsplit(endpoint)
    host = (parts.hostname or "").lower()
    return (parts.scheme == "https" and parts.port in (None, 443) and len(endpoint) <= 1000
            and any(host == h or host.endswith("." + h) for h in PUSH_HOSTS))


def load(db: Session, user_id: int) -> list[dict]:
    try:
        data = json.loads(app_settings.get_setting(db, f"{PREFIX}{user_id}") or "[]")
    except ValueError:
        return []
    return [s for s in data if isinstance(s, dict) and {"endpoint", "p256dh", "auth"} <= s.keys()] \
        if isinstance(data, list) else []


def _save(db: Session, user_id: int, subs: list[dict]) -> None:
    app_settings.set_setting(db, f"{PREFIX}{user_id}", json.dumps(subs[:MAX_SUBS]))
    db.flush()   # następny odczyt w tej samej sesji widzi zapis (get_setting czyta po kluczu)


def subscribe(db: Session, user_id: int, endpoint: str, p256dh: str, auth: str) -> None:
    """Dodaje urządzenie (najnowsze na początku). ValueError = adres spoza znanych usług push / złe klucze."""
    if not allowed_endpoint(endpoint):
        raise ValueError("Nieobsługiwana usługa push.")
    if len(_b64d(p256dh)) != 65 or len(_b64d(auth)) != 16:
        raise ValueError("Nieprawidłowe klucze subskrypcji.")
    rest = [s for s in load(db, user_id) if s["endpoint"] != endpoint]
    _save(db, user_id, [{"endpoint": endpoint, "p256dh": p256dh, "auth": auth}, *rest])


def unsubscribe(db: Session, user_id: int, endpoint: str | None = None) -> None:
    """Usuwa jedno urządzenie albo (bez adresu) wszystkie urządzenia konta."""
    _save(db, user_id, [s for s in load(db, user_id) if endpoint and s["endpoint"] != endpoint])


def _vapid_header(endpoint: str, key: ec.EllipticCurvePrivateKey) -> str:
    parts = urlsplit(endpoint)
    claims = {"aud": f"{parts.scheme}://{parts.netloc}", "exp": int(time.time()) + TTL_SECONDS,
              "sub": settings.vapid_subject}
    token = jwt.encode(claims, key, algorithm="ES256")
    return f"vapid t={token}, k={public_key()}"


def encrypt(sub: dict, payload: bytes) -> bytes:
    import http_ece
    server_key = ec.generate_private_key(ec.SECP256R1())   # nowy klucz na wiadomość (RFC 8291)
    return http_ece.encrypt(payload, private_key=server_key, dh=_b64d(sub["p256dh"]),
                            auth_secret=_b64d(sub["auth"]), version="aes128gcm")


def send(sub: dict, payload: dict) -> int:
    """Jedna wysyłka; zwraca status HTTP usługi push (404/410 = urządzenie wyrejestrowane)."""
    key = _private_key()
    if key is None or not allowed_endpoint(sub["endpoint"]):
        return 0
    body = encrypt(sub, json.dumps(payload, ensure_ascii=False).encode())
    r = httpx.post(sub["endpoint"], content=body, timeout=10, headers={
        "Content-Encoding": "aes128gcm", "TTL": str(TTL_SECONDS), "Urgency": "high",
        "Authorization": _vapid_header(sub["endpoint"], key)})
    return r.status_code


def _deliver(targets: list[tuple[int, dict]], payload: dict) -> None:
    gone: dict[int, set[str]] = {}
    for user_id, sub in targets:
        try:
            if send(sub, payload) in (404, 410):
                gone.setdefault(user_id, set()).add(sub["endpoint"])
        except Exception as exc:  # noqa: BLE001 — jedno urządzenie nie może zatrzymać reszty
            logger.warning("Push nie wysłany: %s", exc)
    if gone:
        from .database import SessionLocal
        with SessionLocal() as db:
            for user_id, endpoints in gone.items():
                _save(db, user_id, [s for s in load(db, user_id) if s["endpoint"] not in endpoints])
            db.commit()


def subscriptions(db: Session, user_ids: Iterable[int]) -> list[tuple[int, dict]]:
    keys = [f"{PREFIX}{uid}" for uid in set(user_ids)]
    if not keys:
        return []
    out: list[tuple[int, dict]] = []
    for row in db.scalars(select(AppSetting).where(AppSetting.key.in_(keys))):
        uid = int(row.key.removeprefix(PREFIX))
        out += [(uid, s) for s in load(db, uid)]
    return out


def queue(db: Session, kind: str, title: str, container_id: int | None, user_ids: list[int]) -> None:
    """Wołane z notify(): push dla pilnych rodzajów, wysyłka w tle dopiero po commicie."""
    if kind not in URGENT_KINDS or not user_ids or not settings.vapid_private_key:
        return
    targets = subscriptions(db, user_ids)
    if not targets:
        return
    from .notifications import _after_commit, _submit
    payload = {"title": title[:120], "url": f"/kontenery/{container_id}" if container_id else "/",
               "tag": f"{kind}-{container_id or 0}"}
    _after_commit(db, lambda: _submit(_deliver, targets, payload))
