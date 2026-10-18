"""Włącz / wyłącz automat z ekranu Automatyzacje (druga lista PO, pkt 6).

Admin wyłącza automat z harmonogramu jednym przełącznikiem; pętla zadań pomija wtedy jego funkcje
(bez wpisu w dzienniku), a katalog pokazuje stan „wyłączony”. Zapis w AppSetting `automation_disabled`
(lista kluczy), każda zmiana w dzienniku zmian (router). Automatów chroniących dane i bezpieczeństwo
nie da się wyłączyć z ekranu — tylko konfiguracją wdrożenia (LOCKED)."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from . import app_settings

SETTING_KEY = "automation_disabled"
# RODO (dane kierowców), retencja logów, test kopii, strażnik automatów — wyłączenie = ryzyko, nie wygoda
LOCKED = frozenset({"driver_data_purge", "retention", "verify_backup", "orphan_files", "watchdog"})


def disabled(db: Session) -> set[str]:
    raw = app_settings.get_setting(db, SETTING_KEY)
    try:
        keys = json.loads(raw) if raw else []
    except ValueError:
        keys = []
    return {k for k in keys if isinstance(k, str)} - LOCKED


def set_enabled(db: Session, key: str, enabled: bool) -> bool:
    """Zwraca poprzedni stan (True = był włączony). ValueError: nieznany albo chroniony automat."""
    from .automation_catalog import SCHEDULED
    if key not in {s.key for s in SCHEDULED}:
        raise ValueError(f"nieznany automat: {key}")
    if key in LOCKED:
        raise ValueError(f"automatu {key} nie można wyłączyć z ekranu (ochrona danych / bezpieczeństwo)")
    current = disabled(db)
    was_enabled = key not in current
    current = current - {key} if enabled else current | {key}
    app_settings.set_setting(db, SETTING_KEY, json.dumps(sorted(current)))
    return was_enabled


def fn_disabled(db: Session, fn_name: str) -> bool:
    """Czy funkcja zadania należy do wyłączonego automatu (pętla zadań pomija przebieg)."""
    keys = disabled(db)
    if not keys:
        return False
    from .automation_catalog import SCHEDULED
    return any(fn_name in s.fns and s.key in keys for s in SCHEDULED)
