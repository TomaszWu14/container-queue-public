"""Ekran „Automatyzacje” (US-032/US-033): katalog automatów z licznikami i stanem;
założenia minut do licznika oszczędności (US-034) zmienia admin.

Dostęp jak pulpit logistyki (admin, logistyka; konto demo to logistyka). Liczniki pętli tła są
systemowe (bez danych spółek); obiegi z poczty liczone w zakresie użytkownika — patrz
`automation_catalog._event_rows`."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import httpx

from .. import ai_quality, automation_catalog, automation_switch, automation_events, automation_savings, demo_simulation, process_mining
from ..config import settings
from ..audit import record
from ..database import get_db
from ..deps import AdminOnly as admin_only
from ..deps import Editors as editors
from ..models import User

router = APIRouter(prefix="/api", tags=["automations"])


class EnabledIn(BaseModel):
    enabled: bool


class MinutesIn(BaseModel):
    minutes: dict[str, int] = Field(default_factory=dict)


@router.get("/automations")
def list_automations(db: Session = Depends(get_db), user: User = editors) -> dict:
    return automation_catalog.catalog(db, user)


@router.get("/automations/ai-quality")
def ai_reading_quality(weeks: int = Query(8, ge=2, le=26), db: Session = Depends(get_db),
                       user: User = editors) -> dict:
    """US-037: odczyt faktur — reguły / ML / człowiek tydzień po tygodniu i trafność podpowiedzi
    modelu wg pewności; tylko paczki kontenerów w zakresie użytkownika."""
    return ai_quality.quality(db, user, weeks=weeks)


@router.get("/automations/simulate-day")
def simulate_day(db: Session = Depends(get_db), user: User = editors) -> dict:
    """US-040: „Symuluj dzień” — prawdziwe funkcje automatów na danych użytkownika, BEZ zapisu
    (GET; konto demo pozostaje tylko do odczytu)."""
    return demo_simulation.simulate(db, user)


@router.get("/automations/process")
def process_flow(days: int = Query(90, ge=14, le=365), db: Session = Depends(get_db),
                 user: User = editors) -> dict:
    """US-038: czas w etapach procesu z historii statusów, cofnięcia i kontenery utknięte dłużej
    niż zwykle (90. percentyl etapu); tylko kontenery w zakresie użytkownika."""
    return process_mining.analyze(db, user, days=days)


@router.get("/automations/ai-quality/mistakes")
def ai_mistakes(limit: int = Query(15, ge=1, le=50), db: Session = Depends(get_db),
                user: User = editors) -> list[dict]:
    """Druga lista PO, pkt 8: pozycje faktur, w których człowiek poprawił podpowiedź modelu (zakres spółek)."""
    return ai_quality.mistakes(db, user, limit=limit)


@router.put("/automations/minutes")
def set_minutes(body: MinutesIn, db: Session = Depends(get_db), user: User = admin_only) -> dict:
    bad = [k for k, v in body.minutes.items() if not 0 <= v <= automation_savings.MAX_MINUTES]
    if bad:
        raise HTTPException(422, f"Minuty poza zakresem 0–{automation_savings.MAX_MINUTES}: {', '.join(bad)}")
    before = automation_savings.minutes(db)
    try:
        after = automation_savings.save_minutes(db, body.minutes)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    for key, value in body.minutes.items():
        if before[key] != value:
            record(db, entity_type="app_settings", entity_id=0, field=f"automation_minutes.{key}",
                   old_value=before[key], new_value=value, user=user)
    db.commit()
    return {"minutes": after}


@router.post("/automations/test-event")
def send_test_event(db: Session = Depends(get_db), user: User = admin_only) -> dict:
    """US-035: zdarzenie testowe do n8n wysłane od razu (nie w tle), żeby admin zobaczył wynik.

    Odpowiedź bez adresu webhooka i treści błędu (adres n8n bywa sekretem) — tylko kod HTTP
    albo rodzaj błędu; szczegóły w dzienniku zadań (job „n8n_events”)."""
    url = settings.automation_webhook_url
    if not url:
        raise HTTPException(409, "Webhook zdarzeń nie jest skonfigurowany (AUTOMATION_WEBHOOK_URL).")
    payload = automation_events.envelope("test", "Zdarzenie testowe z ekranu Automatyzacje",
                                         f"Wysłał: {user.login}")
    result: dict = {"ok": True, "status_code": None, "error": "", "id": payload["id"],
                    "signed": bool(settings.automation_webhook_secret)}
    try:
        result["status_code"] = automation_events.post(url, payload)
    except httpx.HTTPStatusError as exc:
        result.update(ok=False, status_code=exc.response.status_code, error="HTTPStatusError")
    except Exception as exc:  # noqa: BLE001 — wynik dla admina, nie błąd serwera
        result.update(ok=False, error=type(exc).__name__)
    # ślad w dzienniku zmian: kto i kiedy wysłał zdarzenie na zewnątrz (bez adresu webhooka)
    record(db, entity_type="automation", entity_id=0, field="test_event", old_value=None,
           new_value=f"HTTP {result['status_code']}" if result["status_code"] else result["error"],
           user=user, note=payload["id"])
    db.commit()
    return result


@router.put("/automations/{key}/enabled")
def set_automation_enabled(key: str, body: EnabledIn, db: Session = Depends(get_db),
                           user: User = admin_only) -> dict:
    """Druga lista PO, pkt 6: admin włącza / wyłącza automat z harmonogramu; zmiana w dzienniku zmian.
    Automatów chroniących dane (RODO, retencja, kopia, strażnik) nie da się wyłączyć — 422."""
    try:
        was = automation_switch.set_enabled(db, key, body.enabled)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if was != body.enabled:
        record(db, entity_type="automation", entity_id=0, field=f"enabled.{key}",
               old_value="tak" if was else "nie", new_value="tak" if body.enabled else "nie", user=user)
    db.commit()
    return {"key": key, "enabled": body.enabled}
