"""Kreator reguł bez kodu (US-036, pomysł 8 PO): „gdy warunek → powiadom”, ustawiane w panelu.

Reguły to lista w ustawieniach aplikacji (AppSetting `automation_rules`, JSON) — bez nowej
tabeli: kilka–kilkanaście reguł, zmiana zawsze całą listą przez admina (z audytem).
Warunki to zamknięty katalog (`CONDITIONS`) z parametrami: dni i ewentualnie status —
żadnego wolnego tekstu wykonywanego jako kod, żadnych pól wybieranych z bazy po nazwie.

Pętla tła `automation_rules` (co godzinę) sprawdza włączone reguły na otwartych kontenerach
i wysyła powiadomienie obserwującym kontener albo adminom; jedno na regułę, kontener i dzień.
Kanały wybiera reguła (`channels`, US-063): dzwonek, e-mail, karta w Teams, zdarzenie do n8n —
domyślnie wszystkie, jak pozostałe alerty; matryca kanałów per rola nadal obowiązuje.
"""
from __future__ import annotations

import datetime
import json
import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from . import app_settings
from .models import (Container, ContainerStatus, Notification, Role, User, pl_midnight_utc,
                     today_pl, utcnow)

SETTING_KEY = "automation_rules"
MAX_RULES = 20
MAX_PER_RULE = 200          # bezpiecznik: reguła trafiająca setki kontenerów to raczej błąd ustawienia
NOTIFY_KIND = "rule"

Condition = Literal["eta_passed", "notify_soon_status", "no_driver", "plan_unconfirmed"]
CONDITIONS: tuple[str, ...] = ("eta_passed", "notify_soon_status", "no_driver", "plan_unconfirmed")
FLOW = list(ContainerStatus)
DONE = (ContainerStatus.DOSTARCZONY, ContainerStatus.ZREALIZOWANY)
Channel = Literal["bell", "email", "teams", "n8n"]
CHANNELS: tuple[Channel, ...] = ("bell", "email", "teams", "n8n")


class Rule(BaseModel):
    id: str = ""
    name: str = Field(min_length=1, max_length=80)
    enabled: bool = True
    condition: Condition
    days: int = Field(ge=0, le=60)
    status: ContainerStatus | None = None     # tylko notify_soon_status: „wciąż przed tym etapem”
    notify: Literal["watchers", "admins"] = "watchers"
    channels: list[Channel] = Field(default_factory=lambda: list(CHANNELS))

    @field_validator("name")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nazwa nie może być pusta")
        return v

    @field_validator("channels")
    @classmethod
    def _channels(cls, v: list[Channel]) -> list[Channel]:
        if not v:
            raise ValueError("wybierz co najmniej jeden kanał")
        return [c for c in CHANNELS if c in v]          # bez powtórzeń, stała kolejność

    @model_validator(mode="after")
    def _status_needed(self) -> Rule:
        if self.condition == "notify_soon_status" and self.status is None:
            raise ValueError("warunek „awizacja blisko, a status przed etapem” wymaga statusu")
        return self


def load(db: Session) -> list[Rule]:
    raw = app_settings.get_setting(db, SETTING_KEY)
    try:
        data = json.loads(raw) if raw else []
    except ValueError:
        return []
    rules = []
    for item in data if isinstance(data, list) else []:
        try:
            rules.append(Rule.model_validate(item))
        except ValueError:
            continue          # uszkodzony wpis nie wyłącza pozostałych reguł
    return rules


def save(db: Session, rules: list[Rule]) -> list[Rule]:
    if len(rules) > MAX_RULES:
        raise ValueError(f"najwyżej {MAX_RULES} reguł")
    for rule in rules:
        rule.id = rule.id or uuid.uuid4().hex[:12]
    app_settings.set_setting(db, SETTING_KEY,
                             json.dumps([r.model_dump(mode="json") for r in rules], ensure_ascii=False))
    return rules


def clause(rule: Rule, today: datetime.date, now: datetime.datetime):
    """Warunek reguły jako wyrażenie SQL na Container (tylko otwarte, niedostarczone)."""
    base = and_(Container.open_in_queue(), Container.status.notin_(DONE))
    horizon = today + datetime.timedelta(days=rule.days)
    if rule.condition == "eta_passed":
        return and_(base, Container.eta.is_not(None),
                    Container.eta <= today - datetime.timedelta(days=rule.days))
    if rule.condition == "notify_soon_status":
        before = FLOW[:FLOW.index(rule.status)] if rule.status else []
        return and_(base, Container.notify_date.is_not(None), Container.notify_date >= today,
                    Container.notify_date <= horizon, Container.status.in_(before))
    if rule.condition == "no_driver":
        return and_(base, Container.notify_date.is_not(None), Container.notify_date >= today,
                    Container.notify_date <= horizon,
                    or_(Container.driver_name.is_(None), Container.driver_name == ""))
    # plan_unconfirmed: plan wysłany do spedycji N dni temu i nadal bez potwierdzenia
    return and_(base, Container.planning_sent_at.is_not(None),
                Container.planning_sent_at <= now - datetime.timedelta(days=rule.days),
                Container.planning_confirmed_at.is_(None))


def matching(db: Session, rule: Rule, scope=None, today: datetime.date | None = None,
             now: datetime.datetime | None = None, limit: int = MAX_PER_RULE) -> list[Container]:
    """Kontenery spełniające regułę dziś; `scope` = funkcja zawężająca zapytanie (izolacja)."""
    q = select(Container).where(clause(rule, today or today_pl(), now or utcnow()))
    if scope is not None:
        q = scope(q)
    return list(db.scalars(q.order_by(Container.id).limit(limit)))


def title(rule: Rule, container: Container) -> str:
    return f"Reguła „{rule.name}”: {container.container_no}"


def run_rules(db: Session, today: datetime.date | None = None) -> int:
    """Pętla tła: każda włączona reguła → powiadomienie raz dziennie na kontener. Zwraca liczbę
    powiadomień (efekt automatu na ekranie Automatyzacje)."""
    from .notifications import container_watchers, notify
    today = today or today_pl()
    since = pl_midnight_utc(today)
    sent = 0
    for rule in (r for r in load(db) if r.enabled):
        admins = None
        for container in matching(db, rule, today=today):
            text = title(rule, container)
            if db.scalar(select(Notification.id).where(
                    Notification.kind == NOTIFY_KIND, Notification.container_id == container.id,
                    Notification.title == text, Notification.created_at >= since).limit(1)):
                continue
            if rule.notify == "admins":
                admins = admins if admins is not None else list(db.scalars(
                    select(User).where(User.is_active, User.role == Role.admin)))
                users = admins
            else:
                users = container_watchers(db, container)
            sent += notify(db, users, kind=NOTIFY_KIND, title=text, container_id=container.id,
                           channels=rule.channels)
    db.commit()
    return sent
