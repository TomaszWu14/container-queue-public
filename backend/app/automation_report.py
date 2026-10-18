"""Tygodniowy raport automatów (druga lista PO, pkt 9): w poniedziałek 8:00–9:00 (czas PL) każdy, kto widzi
ekran Automatyzacje (admin, logistyka — Z-023), dostaje jedno powiadomienie (dzwonek + e-mail wg matrycy
kanałów): zaoszczędzone godziny z ostatnich 7 dni, liczba przebiegów i efektów, automaty wymagające uwagi
i trzy automaty, które oszczędziły najwięcej. Liczby z tego samego katalogu co ekran (zakres użytkownika)."""
from __future__ import annotations

import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Notification, Role, User, pl_midnight_utc, utcnow
from .models.enums import PL_TZ

NOTIFY_KIND = "automation-weekly"
TOP = 3


def body(cat: dict) -> str:
    s = cat["summary"]
    lines = [f"Zaoszczędzone: ok. {s['hours_saved']} h pracy ręcznej (założenia minut na ekranie Automatyzacje).",
             f"Przebiegi: {s['runs']}, efekty: {s['effects']}, automaty aktywne: {s['active']} z {s['total']}."]
    attention = [i for i in cat["items"] if i["status"] in ("error", "late")]
    lines.append("Wymagają uwagi: " + (", ".join(f"{i['key']} ({i['status']})" for i in attention)
                                      if attention else "brak."))
    best = sorted((i for i in cat["items"] if i["minutes_saved"]), key=lambda i: -i["minutes_saved"])[:TOP]
    if best:
        lines.append("Najwięcej oszczędziły: " + ", ".join(
            f"{i['key']} ({round(i['minutes_saved'] / 60, 1)} h)" for i in best) + ".")
    return "\n".join(lines)


def check_automation_weekly_report(db: Session, now: datetime.datetime | None = None) -> int:
    from .automation_catalog import catalog
    from .notifications import notify
    now = now or utcnow()
    local = now.replace(tzinfo=datetime.UTC).astimezone(PL_TZ)
    if local.weekday() != 0 or local.hour != 8:
        return 0
    already = set(db.scalars(select(Notification.user_id).where(
        Notification.kind == NOTIFY_KIND, Notification.created_at >= pl_midnight_utc(local.date()))))
    sent = 0
    for user in db.scalars(select(User).where(User.is_active, User.role.in_((Role.admin, Role.logistics)))):
        if user.id in already:
            continue
        cat = catalog(db, user, now=now)
        title = f"Automaty w tym tygodniu: ok. {cat['summary']['hours_saved']} h zaoszczędzone"
        sent += notify(db, [user], kind=NOTIFY_KIND, title=title, body=body(cat), broadcast=False)
    db.commit()
    return sent
