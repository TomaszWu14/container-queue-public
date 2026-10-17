"""Ekran „Automatyzacje” (US-032/US-033): katalog automatów z licznikami i stanem;
założenia minut do licznika oszczędności (US-034) zmienia admin.

Dostęp jak pulpit logistyki (admin, logistyka; konto demo to logistyka). Liczniki pętli tła są
systemowe (bez danych spółek); obiegi z poczty liczone w zakresie użytkownika — patrz
`automation_catalog._event_rows`."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import automation_catalog, automation_savings
from ..audit import record
from ..database import get_db
from ..deps import AdminOnly as admin_only
from ..deps import Editors as editors
from ..models import User

router = APIRouter(prefix="/api", tags=["automations"])


class MinutesIn(BaseModel):
    minutes: dict[str, int] = Field(default_factory=dict)


@router.get("/automations")
def list_automations(db: Session = Depends(get_db), user: User = editors) -> dict:
    return automation_catalog.catalog(db, user)


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
