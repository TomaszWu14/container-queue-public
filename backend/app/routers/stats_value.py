"""Panel „Ile to oszczędza” (pomysł 2 PO, mierniki z docs/analiza/WIZJA.md): wartość aplikacji liczona
z jej własnych danych za ostatnie N dni, w zakresie użytkownika (izolacja: scope_containers).

Jedyne założenie to minuty pracy na jedną zmianę zapisaną w aplikacji zamiast w Excelu i mailach
(`MINUTES_PER_CHANGE`, Z-020 do potwierdzenia przez PO) — zwracane w odpowiedzi, żeby ekran pokazał je
jawnie. Reszta to zliczenia: dostawy na czas, komplet dokumentów, ostrzeżenia o karach za przestój."""
import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import Editors as editors
from ..deps import NonWarehouseViewers as non_warehouse
from ..deps import scope_containers
from ..models import AuditLog, Container, Notification, User, today_pl, utcnow

# sub-router bez prefiksu — podpinany w routers/containers.py (prefiks /api)
router = APIRouter()

MINUTES_PER_CHANGE = 3   # Z-020: zmiana w aplikacji vs wpis w Excelu + mail do zainteresowanych


@router.get("/stats/value")
def value_panel(days: int = Query(30, ge=7, le=365), db: Session = Depends(get_db),
                user: User = editors) -> dict:
    from .customs import missing_document_types_batch   # leniwie: customs importuje containers
    since = utcnow() - datetime.timedelta(days=days)
    ids = select(Container.id)
    scoped = scope_containers(ids, user).subquery()

    changes = db.scalar(select(func.count()).select_from(AuditLog).where(
        AuditLog.entity_type == "containers", AuditLog.entity_id.in_(select(scoped.c.id)),
        AuditLog.created_at >= since, AuditLog.user_id.is_not(None))) or 0

    delivered = db.execute(select(AuditLog.created_at, Container.notify_date)
                           .join(Container, Container.id == AuditLog.entity_id)
                           .where(AuditLog.entity_type == "containers", AuditLog.field == "status",
                                  AuditLog.new_value == "DOSTARCZONY", AuditLog.created_at >= since,
                                  Container.id.in_(select(scoped.c.id)))).all()
    on_time = sum(1 for at, planned in delivered if planned is None or at.date() <= planned)

    in_flow = db.scalars(scope_containers(select(Container).where(
        Container.open_in_queue(), Container.customs_agency_id.is_not(None)), user)).all()
    missing = missing_document_types_batch(db, list(in_flow))
    complete = sum(1 for c in in_flow if not missing.get(c.id))

    warned = db.scalar(select(func.count(func.distinct(Notification.container_id))).where(
        Notification.kind == "demurrage", Notification.created_at >= since,
        Notification.container_id.in_(select(scoped.c.id)))) or 0

    return {
        "days": days,
        "changes": changes,
        "minutes_per_change": MINUTES_PER_CHANGE,
        "hours_saved": round(changes * MINUTES_PER_CHANGE / 60, 1),
        "delivered": len(delivered), "delivered_on_time": on_time,
        "docs_in_flow": len(in_flow), "docs_complete": complete,
        "demurrage_warned": warned,
    }


@router.get("/stats/demurrage-risk")
def demurrage_risk(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
                   user: User = non_warehouse) -> list[dict]:
    """Pomysł 10 PO: kontenery z ryzykiem kary za przestój i powodem (zakres jak pulpit)."""
    from ..demurrage_risk import demurrage_risks
    open_containers = db.scalars(scope_containers(select(Container).where(Container.open_in_queue()),
                                                  user)).all()
    return demurrage_risks(db, open_containers, today_pl())[:limit]
