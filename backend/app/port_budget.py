"""Budżet kosztów transportu i portu na spółkę i miesiąc (czwarta lista PO, pkt 7, US-084).

Admin wpisuje miesięczny budżet spółki w EUR. Zużycie = suma faktur transportowych (B/L) spółki z bieżącego
miesiąca kalendarzowego (data dodania faktury, czas PL), bez faktur ODRZUCONYCH; inne waluty przeliczane kursem
NBP (bez kursu — pomijane i liczone osobno). Prognoza = zużycie / dni, które minęły × dni miesiąca.
Stan: „ok”, „uwaga” (prognoza ≥ 90% budżetu), „przekroczony” (zużycie > budżetu). Co liczymy jako koszt i próg
90% to założenie Z-044. Zapis budżetu bez migracji: ustawienie `port_budget:{company_id}`.
Tylko podgląd i ostrzeżenie na ekranie — nic nie blokuje wprowadzania faktur."""
from __future__ import annotations

import calendar
import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import app_settings, nbp
from .models import Company, FreightInvoice, pl_midnight_utc, today_pl

PREFIX = "port_budget:"
WARN_RATIO = 0.9


def get_budget(db: Session, company_id: int) -> float | None:
    raw = app_settings.get_setting(db, f"{PREFIX}{company_id}")
    try:
        value = float(raw) if raw else None
    except ValueError:
        return None
    return value if value and value > 0 else None


def set_budget(db: Session, company_id: int, amount: float | None) -> None:
    app_settings.set_setting(db, f"{PREFIX}{company_id}", f"{amount:.2f}" if amount else "")


def _eur(amount: float, currency: str, rates: dict[str, float]) -> float | None:
    if (currency or "EUR").upper() == "EUR":
        return amount
    converted = nbp.convert(amount, currency, ("EUR",), rates=rates, as_of=None)["converted"] if rates else {}
    return converted.get("EUR")


def status(db: Session, user, today: datetime.date | None = None) -> dict:
    from .deps import scope_company
    today = today or today_pl()
    first = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    rates, _ = nbp.get_rates()
    companies = db.execute(scope_company(select(Company.id, Company.name).order_by(Company.name),
                                         Company.id, user)).all()
    invoices = db.execute(scope_company(
        select(FreightInvoice.company_id, FreightInvoice.amount, FreightInvoice.currency)
        .where(FreightInvoice.created_at >= pl_midnight_utc(first), FreightInvoice.status != "ODRZUCONA",
               FreightInvoice.amount.is_not(None)), FreightInvoice.company_id, user)).all()
    spent: dict[int, float] = {}
    unconverted: dict[int, int] = {}
    for company_id, amount, currency in invoices:
        eur = _eur(float(amount), currency, rates)
        if eur is None:
            unconverted[company_id] = unconverted.get(company_id, 0) + 1
            continue
        spent[company_id] = spent.get(company_id, 0.0) + eur
    rows = []
    for cid, name in companies:
        budget = get_budget(db, cid)
        used = round(spent.get(cid, 0.0), 2)
        forecast = round(used / today.day * days_in_month, 2)
        state = ("none" if budget is None else "over" if used > budget
                 else "warn" if forecast >= WARN_RATIO * budget else "ok")
        rows.append({"company_id": cid, "company": name, "budget_eur": budget, "spent_eur": used,
                     "forecast_eur": forecast, "state": state, "unconverted": unconverted.get(cid, 0)})
    return {"month": first.isoformat()[:7], "day": today.day, "days_in_month": days_in_month,
            "warn_ratio": WARN_RATIO, "companies": rows}
