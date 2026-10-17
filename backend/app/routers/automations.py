"""Ekran „Automatyzacje” (US-032/US-033): katalog automatów z licznikami i stanem.

Dostęp jak pulpit logistyki (admin, logistyka; konto demo to logistyka). Liczniki pętli tła są
systemowe (bez danych spółek); obiegi z poczty liczone w zakresie użytkownika — patrz
`automation_catalog._event_rows`."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import automation_catalog
from ..database import get_db
from ..deps import Editors as editors
from ..models import User

router = APIRouter(prefix="/api", tags=["automations"])


@router.get("/automations")
def list_automations(db: Session = Depends(get_db), user: User = editors) -> dict:
    return automation_catalog.catalog(db, user)
