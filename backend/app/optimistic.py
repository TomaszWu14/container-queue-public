"""Ochrona przed cichym nadpisaniem przejść statusu (US-003, ADR-0003, ryzyko R-02).

Formularze wysyłają `expected_updated_at` (DB-005, containers_common.check_not_modified). Przejście
statusu sprawdza tylko swoją kolumnę: klient podaje status, który widział, a serwer zajmuje wiersz
warunkowym UPDATE-em — dwa równoległe kliknięcia na tym samym stanie nie przejdą oba, a niezwiązana
zmiana (notatka, tracking) nie daje fałszywego konfliktu. Brak oczekiwanej wartości = bez kontroli."""
from typing import Any, cast

from fastapi import HTTPException, status
from sqlalchemy import CursorResult, select, update
from sqlalchemy.orm import Session


def _label(value: Any) -> str:
    return str(getattr(value, "value", value) or "—").replace("_", " ")


def claim_expected_state(db: Session, model, row_id: int, column, expected: Any) -> None:
    """409 `state_changed`, gdy `column` wiersza nie ma już wartości `expected`."""
    if expected is None:
        return
    res = cast(CursorResult, db.execute(
        update(model).where(model.id == row_id, column == expected)
        .values({column.key: expected}).execution_options(synchronize_session=False)))
    if res.rowcount == 1:
        return
    current = db.scalar(select(column).where(model.id == row_id))
    raise HTTPException(status.HTTP_409_CONFLICT, {
        "code": "state_changed",
        "message": f"Ktoś zmienił status w międzyczasie (teraz: {_label(current)}) — "
                   "odśwież i zdecyduj ponownie.",
        "current": getattr(current, "value", current)})
