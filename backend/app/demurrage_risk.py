"""Ryzyko kary za przestój (demurrage) z wyjaśnieniem (pomysł 10 PO): zamiast samej daty — dlaczego
grozi kara i co zrobić. Proste, jawne reguły, bez modelu „czarnej skrzynki”:

- `planned_after_deadline`: dostawa zaplanowana po końcu wolnych dni → N dni kary; przesuń na ≤ termin,
- `unplanned_near_deadline`: wolne dni kończą się w ciągu `NEAR_DAYS`, a dostawa nie ma terminu.

Kwot nie liczymy: stawki armatorów nie są przechowywane (notification_alerts.demurrage_window)."""
import datetime
from collections.abc import Sequence

from sqlalchemy.orm import Session

from .models import Container
from .notification_alerts import demurrage_deadlines

NEAR_DAYS = 3


def demurrage_risks(db: Session, containers: Sequence[Container], today: datetime.date) -> list[dict]:
    """Kontenery z ryzykiem kary, najpilniejsze pierwsze (najmniej dni do terminu / najwięcej dni kary)."""
    deadlines = demurrage_deadlines(db, containers)
    out = []
    for c in containers:
        deadline = deadlines.get(c.id)
        if deadline is None or c.status in Container.FINISHED:
            continue
        base = {"container_id": c.id, "container_no": c.container_no, "deadline": deadline.isoformat(),
                "planned": c.notify_date.isoformat() if c.notify_date else None,
                "days_left": (deadline - today).days}
        if c.notify_date and c.notify_date > deadline:
            out.append({**base, "reason": "planned_after_deadline",
                        "days_over": (c.notify_date - deadline).days})
        elif c.notify_date is None and (deadline - today).days <= NEAR_DAYS:
            out.append({**base, "reason": "unplanned_near_deadline", "days_over": max(0, (today - deadline).days)})
    return sorted(out, key=lambda r: (r["days_left"], -r["days_over"]))
