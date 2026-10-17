"""Licznik oszczędności per automat (US-034, pomysł 3 PO; założenie Z-024 do potwierdzenia).

Minuty pracy ręcznej, które zastępuje JEDEN efekt automatu (powiadomienie, przeczytana faktura,
SMS, mail z poczty…). Wartości startowe to jawne założenia zespołu — admin zmienia je w panelu
(ekran „Automatyzacje”), a ekran pokazuje je obok wyniku. Automaty porządkowe (retencja, kopia,
osierocone pliki) mają 0: chronią dane, ale nie zastępują pracy człowieka 1:1.

Efekt automatu z harmonogramu = liczba zwrócona przez jego funkcję (zapis w dzienniku zadań);
obiegu z poczty = liczba przetworzonych maili.
"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from . import app_settings

SETTING_KEY = "automation_minutes"
MAX_MINUTES = 240

# Z-024: minuty na jeden efekt — założenia startowe, do potwierdzenia przez PO
DEFAULT_MINUTES: dict[str, int] = {
    "demurrage": 5,            # ręczne sprawdzenie wolnych dni u armatora i mail do logistyki
    "customs_delay": 5,        # telefon/mail do agencji o stan odprawy
    "missing_docs": 5,         # przejrzenie checklisty dokumentów i przypomnienie
    "forecast": 10,            # zliczenie rozładunków na dzień w Excelu
    "tracking": 3,             # sprawdzenie statku na stronie armatora / w AIS
    "stale_import": 2,
    "pallet_urgent": 5,
    "invoice_ingest": 15,      # przepisanie paczki faktur do zestawienia
    "complaint_drafts": 20,    # przygotowanie szkicu reklamacji
    "complaint_reminders": 3,
    "sms_reminders": 3,        # telefon / SMS do kierowcy
    "daily_digest": 15,        # poranne zebranie dostaw, opóźnień i braków w mail
    "weekly_digest": 10,
    "avizo_maintenance": 0, "driver_data_purge": 2, "retention": 0, "orphan_files": 0,
    "verify_backup": 0, "sharepoint_sync": 10, "congestion": 5,
    "mail_intake": 5,          # zapisanie załączników z maila i przypisanie do kontenera
    "sad_from_mail": 10,       # wgranie draftu SAD i porównanie z fakturami
    "outbound_events": 0,
}


def minutes(db: Session) -> dict[str, int]:
    """Założenia minut: wartości z panelu admina nałożone na domyślne (nieznane klucze pomijane)."""
    raw = app_settings.get_setting(db, SETTING_KEY)
    try:
        saved = json.loads(raw) if raw else {}
    except ValueError:
        saved = {}
    merged = dict(DEFAULT_MINUTES)
    if isinstance(saved, dict):
        merged.update({k: int(v) for k, v in saved.items()
                       if k in DEFAULT_MINUTES and isinstance(v, int) and 0 <= v <= MAX_MINUTES})
    return merged


def save_minutes(db: Session, changes: dict[str, int]) -> dict[str, int]:
    """Zapis zmian admina (tylko znane automaty, 0…MAX_MINUTES); zwraca pełny komplet założeń."""
    unknown = sorted(set(changes) - set(DEFAULT_MINUTES))
    if unknown:
        raise ValueError(f"nieznane automaty: {', '.join(unknown)}")
    current = minutes(db)
    current.update(changes)
    custom = {k: v for k, v in current.items() if v != DEFAULT_MINUTES[k]}
    app_settings.set_setting(db, SETTING_KEY, json.dumps(custom, sort_keys=True))
    return current


def apply(items: list[dict], minutes_by_key: dict[str, int]) -> dict:
    """Dopisuje do pozycji katalogu minuty na efekt i zaoszczędzone minuty; zwraca podsumowanie."""
    total = 0
    for item in items:
        per = minutes_by_key.get(item["key"], 0)
        effects = item["effects"] if item["kind"] == "schedule" else item["runs"]
        saved = (effects or 0) * per
        item["minutes_per_effect"] = per
        item["minutes_saved"] = saved
        total += saved
    return {"minutes_saved": total, "hours_saved": round(total / 60, 1)}
