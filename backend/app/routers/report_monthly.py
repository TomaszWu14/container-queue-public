"""Raport miesięczny dla zarządu (trzecia lista PO, pkt 8): jedna strona do druku / zapisu jako PDF
(„Drukuj → Zapisz jako PDF” w przeglądarce — ten sam wzorzec co pisma reklamacyjne, bez biblioteki PDF).

Liczby z tych samych źródeł co ekrany aplikacji, w zakresie użytkownika: panel „Ile to oszczędza”
(ostatnie 30 dni), przebieg procesu (30 dni), odczyt faktur (4 tygodnie), katalog automatów (7 dni)
i ryzyko kar (dziś). Zestaw pozycji to założenie Z-039 do potwierdzenia przez PO."""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import ai_quality, automation_catalog, process_mining
from ..database import get_db
from ..date_pl import date_pl
from ..demurrage_risk import demurrage_risks
from ..deps import Editors as editors
from ..deps import scope_containers
from ..html_templates import render
from ..models import Container, User, today_pl
from ..print_button import PRINT_SCRIPT
from .stats_value import value_panel

router = APIRouter(prefix="/api", tags=["automations"])
# nazwy etapów jak na ekranie (frontend i18n st_*) — raport drukowany jest po polsku
STAGE_PL = {"ZAPOWIEDZIANY": "Planowanie zakupu", "W_PRODUKCJI": "Produkcja / gotowość",
            "TRANSPORT_WSTEPNY": "Transport wstępny", "W_TRANSPORCIE": "Transport morski",
            "W_PORCIE": "Port docelowy", "ODPRAWA": "Odprawa celna", "AWIZOWANY": "Awizowany",
            "W_DOSTAWIE": "Dostawa krajowa", "DOSTARCZONY": "Przyjęcie na magazyn", "ZREALIZOWANY": "Rozliczone"}
DAYS = 30
TOP_STAGES = 3


@router.get("/reports/monthly", response_class=HTMLResponse)
def monthly_report(db: Session = Depends(get_db), user: User = editors) -> HTMLResponse:
    value = value_panel(days=DAYS, db=db, user=user)
    process = process_mining.analyze(db, user, days=DAYS)
    ai = ai_quality.quality(db, user, weeks=4)
    cat = automation_catalog.catalog(db, user)
    open_containers = db.scalars(scope_containers(select(Container).where(Container.open_in_queue()), user)).all()
    risks = demurrage_risks(db, open_containers, today_pl())
    slow = sorted((s for s in process["stages"] if s.get("median_days") is not None),
                  key=lambda s: -s["median_days"])[:TOP_STAGES]
    attention = [i for i in cat["items"] if i["status"] in ("error", "late")]
    return HTMLResponse(render(
        "reports/monthly.html", stage_pl=STAGE_PL, today=date_pl(today_pl()), days=DAYS, value=value, process=process,
        slow=slow, ai=ai, summary=cat["summary"], attention=attention, open_total=len(open_containers),
        risks_total=len(risks), risks_planned_late=sum(1 for r in risks if r["reason"] == "planned_after_deadline"),
        print_script=PRINT_SCRIPT))
