"""Wyciszenie alertów jednego kontenera dla jednej osoby (trzecia lista PO, pkt 3).

„Nie przypominaj przez N dni” w dzwonku: automatyczne powiadomienia o tym kontenerze nie trafiają do tej
osoby do końca dnia `do` (włącznie, dzień PL). Wzmianki (@) i powiadomienia bez kontenera przychodzą dalej.
Pozostali odbiorcy dostają alert jak zwykle — wyciszenie jest osobiste.

Zapis bez nowej tabeli (bez migracji): ustawienie `alert_mute:{user_id}` z JSON-em {container_id: data};
jeden wiersz na osobę, więc dwie osoby nie nadpisują sobie nawzajem listy. Przeterminowane wpisy
wypadają przy następnym zapisie."""
from __future__ import annotations

import datetime
import json
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import app_settings
from .models import AppSetting, today_pl

PREFIX = "alert_mute:"
DAYS = (1, 3, 7)
MAX_MUTES = 200


def _key(user_id: int) -> str:
    return f"{PREFIX}{user_id}"


def _parse(raw: str | None, today: datetime.date) -> dict[int, datetime.date]:
    try:
        data = json.loads(raw) if raw else {}
    except ValueError:
        return {}
    out: dict[int, datetime.date] = {}
    for cid, until in (data.items() if isinstance(data, dict) else []):
        try:
            day = datetime.date.fromisoformat(str(until))
            out[int(cid)] = day
        except ValueError:
            continue
    return {cid: day for cid, day in out.items() if day >= today}


def load(db: Session, user_id: int, today: datetime.date | None = None) -> dict[int, datetime.date]:
    return _parse(app_settings.get_setting(db, _key(user_id)), today or today_pl())


def _save(db: Session, user_id: int, mutes: dict[int, datetime.date]) -> None:
    keep = dict(sorted(mutes.items(), key=lambda kv: kv[1], reverse=True)[:MAX_MUTES])
    app_settings.set_setting(db, _key(user_id), json.dumps({str(c): d.isoformat() for c, d in keep.items()}))


def mute(db: Session, user_id: int, container_id: int, days: int,
         today: datetime.date | None = None) -> datetime.date:
    if days not in DAYS:
        raise ValueError(f"dni: jedno z {DAYS}")
    today = today or today_pl()
    until = today + datetime.timedelta(days=days)
    mutes = load(db, user_id, today)
    mutes[container_id] = until
    _save(db, user_id, mutes)
    return until


def unmute(db: Session, user_id: int, container_id: int) -> bool:
    mutes = load(db, user_id)
    if container_id not in mutes:
        return False
    del mutes[container_id]
    _save(db, user_id, mutes)
    return True


def muted_users(db: Session, user_ids: Iterable[int], container_id: int,
                today: datetime.date | None = None) -> set[int]:
    """Kto z odbiorców wyciszył ten kontener — jedno zapytanie na całą listę odbiorców."""
    ids = {u for u in user_ids}
    if not ids:
        return set()
    today = today or today_pl()
    rows = db.execute(select(AppSetting.key, AppSetting.value).where(
        AppSetting.key.in_([_key(u) for u in ids]))).all()
    return {int(key[len(PREFIX):]) for key, value in rows if container_id in _parse(value, today)}
