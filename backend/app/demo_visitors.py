"""Bramka „przedstaw się” przed kontem demo: ciasteczko 30 dni i retencja 90 dni.

Dane (imię, nazwisko, firma) zostają na serwerze; w ciasteczku jest tylko podpisane id wpisu.
Nie zapisujemy IP ani user-agenta (minimalizacja danych).
"""
import datetime
import logging
import unicodedata
from typing import cast

import jwt
from sqlalchemy import CursorResult, delete
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import DemoVisitor, utcnow

logger = logging.getLogger(__name__)

VISITOR_COOKIE = "demo_visitor"
COOKIE_DAYS = 30
RETENTION_DAYS = 90
GATE_MESSAGE = "Zanim wejdziesz do wersji demonstracyjnej, przedstaw się, proszę."


def gate_active() -> bool:
    """Bramka działa tylko na instancji demo (są loginy tylko do odczytu) i gdy nie wyłączono."""
    return settings.demo_visitor_gate and bool(settings.demo_readonly_logins.strip())


def clean_field(value: str) -> str:
    """Trim + 2–100 znaków, bez znaków sterujących (ValueError przy naruszeniu)."""
    text = " ".join(value.split()) if value else ""
    if not 2 <= len(text) <= 100:
        raise ValueError("Pole musi mieć od 2 do 100 znaków.")
    if any(unicodedata.category(c).startswith("C") for c in text):
        raise ValueError("Pole zawiera niedozwolone znaki.")
    return text


def purge_expired(db: Session) -> int:
    cutoff = utcnow() - datetime.timedelta(days=RETENTION_DAYS)
    result = db.execute(delete(DemoVisitor).where(DemoVisitor.created_at < cutoff))
    count = cast(CursorResult, result).rowcount  # DELETE zwraca CursorResult
    db.commit()
    return count


def purge_on_startup() -> None:
    try:
        with SessionLocal() as db:
            purge_expired(db)
    except Exception:  # noqa: BLE001 — retencja nie może zatrzymać startu aplikacji
        logger.exception("Retencja demo_visitors nie powiodła się")


def register(db: Session, first_name: str, last_name: str, company: str) -> tuple[DemoVisitor, str]:
    """Zapisuje odwiedzającego (przy okazji czyści stare wpisy) i zwraca podpisany token."""
    purge_expired(db)
    visitor = DemoVisitor(first_name=first_name, last_name=last_name, company=company)
    db.add(visitor)
    db.commit()
    exp = utcnow() + datetime.timedelta(days=COOKIE_DAYS)
    token = jwt.encode({"sub": str(visitor.id), "typ": "demo_visitor", "exp": exp},
                       settings.secret_key, algorithm="HS256")
    return visitor, token


def visitor_id(token: str | None) -> int | None:
    """Id wpisu z podpisanego ciasteczka bramki; None = brak, podróbka, wygasłe albo obcy typ."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        if payload.get("typ") != "demo_visitor":
            return None
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None


def has_valid_cookie(db: Session, token: str | None) -> bool:
    vid = visitor_id(token)
    return vid is not None and db.get(DemoVisitor, vid) is not None
