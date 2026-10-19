"""Przegląd dostępów (czwarta lista PO, pkt 9).

Lista kont do decyzji administratora: aktywne konta nieużywane od STALE_DAYS dni (albo nigdy), konta admina
bez 2FA i konta z dostępem do wszystkich spółek. Blokada zostaje decyzją człowieka — panel ma przycisk
„Zablokuj” (istniejący PATCH użytkownika z audytem), automat niczego sam nie wyłącza.

Raz na kwartał (pierwszy poniedziałek stycznia, kwietnia, lipca i października, 8:00 czasu PL) administratorzy
dostają przypomnienie z podsumowaniem (dzwonek + e-mail wg matrycy kanałów). Konta demo i serwisowe pomijamy."""
from __future__ import annotations

import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .automation_policy import is_service_login
from .models import Notification, Role, User, utcnow
from .models.enums import PL_TZ
from .security import is_demo_login

STALE_DAYS = 90
QUARTER_MONTHS = (1, 4, 7, 10)
NOTIFY_KIND = "access-review"


def _skip(user: User) -> bool:
    return is_demo_login(user.login) or is_service_login(user.login)


def review(db: Session, now: datetime.datetime | None = None) -> dict:
    now = now or utcnow()
    border = now - datetime.timedelta(days=STALE_DAYS)
    users = [u for u in db.scalars(select(User).where(User.is_active).order_by(User.login)) if not _skip(u)]

    def row(u: User, reason: str) -> dict:
        return {"id": u.id, "login": u.login, "full_name": u.full_name, "role": u.role.value,
                "last_seen": u.last_seen.isoformat() if u.last_seen else None, "reason": reason}

    stale = [row(u, "never" if u.last_seen is None else "stale")
             for u in users if u.last_seen is None or u.last_seen < border]
    no_2fa = [row(u, "admin_no_2fa") for u in users if u.role == Role.admin and not u.totp_secret]
    all_companies = [row(u, "all_companies") for u in users if u.view_all_companies and u.role != Role.admin]
    return {"stale_days": STALE_DAYS, "active": len(users), "stale": stale,
            "admins_without_2fa": no_2fa, "all_companies": all_companies}


def is_review_day(now: datetime.datetime) -> bool:
    local = now.replace(tzinfo=datetime.UTC).astimezone(PL_TZ)
    return local.month in QUARTER_MONTHS and local.weekday() == 0 and local.day <= 7 and local.hour == 8


def check_access_review(db: Session, now: datetime.datetime | None = None) -> int:
    """Kwartalne przypomnienie dla adminów (dedup: jedno na admina w tygodniu)."""
    from .notifications import notify
    now = now or utcnow()
    if not is_review_day(now):
        return 0
    # okno to jedna godzina jednego dnia — przypomnienie z ostatnich 7 dni oznacza „już wysłane”
    already = set(db.scalars(select(Notification.user_id).where(
        Notification.kind == NOTIFY_KIND, Notification.created_at >= utcnow() - datetime.timedelta(days=7))))
    admins = [u for u in db.scalars(select(User).where(User.is_active, User.role == Role.admin))
              if u.id not in already and not _skip(u)]
    if not admins:
        return 0
    r = review(db, now)
    title = f"Kwartalny przegląd dostępów: {len(r['stale'])} kont do sprawdzenia"
    body = (f"Konta bez logowania od {STALE_DAYS} dni lub nigdy: {len(r['stale'])}. "
            f"Admini bez 2FA: {len(r['admins_without_2fa'])}. "
            f"Konta z dostępem do wszystkich spółek (poza adminami): {len(r['all_companies'])}. "
            "Szczegóły i blokada jednym kliknięciem: Administracja → Użytkownicy → Przegląd dostępów.")
    sent = notify(db, admins, kind=NOTIFY_KIND, title=title, body=body, broadcast=False)
    db.commit()
    return sent
