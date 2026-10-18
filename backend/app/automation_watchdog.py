"""Strażnik automatów (druga lista PO, pkt 7): automat z harmonogramu, który się spóźnia (brak udanego
przebiegu dłużej niż jego interwał + zapas `automation_catalog.JOB_GRACE_S`), zapala dzwonek adminów —
raz dziennie na automat. Awarie pojedynczych przebiegów zgłasza już `applog.flush` (dzwonek „system-error”);
tu łapiemy ciszę: pętla stanęła, wątek padł, zadanie wisi."""
from __future__ import annotations

import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .date_pl import date_pl
from .models import Notification, Role, User, pl_midnight_utc, to_pl_date, utcnow

NOTIFY_KIND = "automation-late"


def check_late_automations(db: Session, now: datetime.datetime | None = None) -> int:
    from .automation_catalog import _scheduled_rows
    from .notifications import notify
    now = now or utcnow()
    since = pl_midnight_utc(to_pl_date(now))
    late = [r for r in _scheduled_rows(db, now) if r["status"] == "late"]
    if not late:
        return 0
    admins = list(db.scalars(select(User).where(User.is_active, User.role == Role.admin)))
    sent = 0
    for row in late:
        title = f"Automat się spóźnia: {row['key']}"
        if db.scalar(select(Notification.id).where(
                Notification.kind == NOTIFY_KIND, Notification.title == title,
                Notification.created_at >= since).limit(1)):
            continue
        last = date_pl(row["last_ok_at"], time=True) if row["last_ok_at"] else "nigdy"
        body = (f"Ostatni udany przebieg: {last}. Sprawdź ekran Automatyzacje i dziennik zadań "
                "(Administracja → Logi).")
        sent += notify(db, admins, kind=NOTIFY_KIND, title=title, body=body)
    db.commit()
    return sent
