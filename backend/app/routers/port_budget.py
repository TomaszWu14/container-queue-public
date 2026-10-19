"""Budżet kosztów transportu i portu (US-084): podgląd dla czytających faktury, zmiana tylko admin."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import port_budget
from ..audit import record
from ..database import get_db
from ..deps import AdminOnly as admin_only
from ..deps import PurchasingReaders as freight_readers
from ..models import Company, User

router = APIRouter(prefix="/api", tags=["budżet"])


class BudgetIn(BaseModel):
    amount_eur: float | None = Field(default=None, ge=0, le=100_000_000)   # puste / 0 = bez budżetu


@router.get("/budgets/port")
def port_budget_view(db: Session = Depends(get_db), user: User = freight_readers) -> dict:
    """Budżet, zużycie i prognoza miesiąca na spółkę (faktury transportowe, US-084)."""
    return port_budget.status(db, user)


@router.put("/budgets/port/{company_id}")
def port_budget_set(company_id: int, body: BudgetIn, db: Session = Depends(get_db),
                    user: User = admin_only) -> dict:
    """Ustawienie miesięcznego budżetu spółki w EUR (z audytem)."""
    if db.get(Company, company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie znaleziono spółki.")
    old = port_budget.get_budget(db, company_id)
    port_budget.set_budget(db, company_id, body.amount_eur or None)
    record(db, entity_type="companies", entity_id=company_id, field="port_budget_eur",
           old_value=None if old is None else f"{old:.2f}",
           new_value=f"{body.amount_eur:.2f}" if body.amount_eur else None, user=user, note="budżet miesięczny")
    db.commit()
    return {"company_id": company_id, "budget_eur": port_budget.get_budget(db, company_id)}
