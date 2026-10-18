"""Asystent bez modelu AI (US-039, pomysł 15 PO): odpowiedź złożona z szablonu i przykładowe pytania.

Na serwerze bez Ollamy (np. instancja demo) asystent dalej zbiera fakty z bazy — tu składamy z nich
jedno, dwa zdania po polsku według stałego szablonu. Odpowiedź jest wprost oznaczona jako szablon
(`answer_source="template"`), żeby nikt nie wziął jej za wynik modelu językowego.

Przykładowe pytania budujemy z danych, które użytkownik i tak widzi (scope_containers; materiały
tylko dla ról z dostępem do kartoteki) — klik w podpowiedź od razu daje odpowiedź z faktami."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Container, Material, Role, User
from .tracking.timeline import _STATUS_PL

MAX_EXAMPLES = 3
MATERIAL_ROLES = (Role.admin, Role.logistics, Role.purchasing)   # jak GET /api/materials

_CUSTOMS_PL = {
    "BRAK": "nie zlecona", "DOKUMENTY_KOMPLETNE": "dokumenty kompletne", "ZLECONA": "zlecona agencji",
    "DRAFT_WYSLANY": "draft zgłoszenia wysłany", "DRAFT_POTWIERDZONY": "draft potwierdzony",
    "ODPRAWIONY": "odprawiony", "ZWOLNIONY": "towar zwolniony", "ROZLICZONY": "rozliczona",
}


def _container_sentence(f: dict) -> str:
    parts = [f"Kontener {f['kontener']}"]
    if f.get("status"):
        parts.append(f"etap {_STATUS_PL.get(f['status'], f['status'])}")
    if f.get("statek"):
        parts.append(f"statek {f['statek']}")
    if f.get("eta"):
        parts.append(f"ETA {f['eta']}")
    parts.append(f"awizacja {f['awizacja']}" if f.get("awizacja") else "bez awizacji")
    if f.get("odprawa"):
        parts.append(f"odprawa: {_CUSTOMS_PL.get(f['odprawa'], f['odprawa'])}")
    if f.get("magazyn"):
        parts.append(f"magazyn {f['magazyn']}")
    return ", ".join(parts) + "."


def _material_sentence(f: dict) -> str:
    text = f"Materiał {f['ref']}: {f.get('nazwa_pl') or f.get('nazwa_en') or 'bez nazwy'}"
    extra = [x for x in (f"JM {f['jm']}" if f.get("jm") else "", f"CN {f['cn']}" if f.get("cn") else "") if x]
    return text + (f" ({', '.join(extra)})" if extra else "") + "."


def answer(facts: dict) -> str | None:
    """Zdania z faktów albo None, gdy faktów brak (wtedy interfejs mówi „nie ma w systemie”)."""
    lines = [_container_sentence(f) for f in facts.get("kontenery", [])]
    lines += [_material_sentence(f) for f in facts.get("materialy", [])]
    return "\n".join(lines) or None


def examples(db: Session, user: User) -> list[str]:
    from .deps import scope_containers
    numbers = db.scalars(scope_containers(
        select(Container.container_no).where(Container.open_in_queue(), Container.container_no != "")
        .order_by(Container.eta.is_(None), Container.eta, Container.id), user).limit(2)).all()
    out = [f"Jaki jest status {numbers[0]}?"] if numbers else []
    if len(numbers) > 1:
        out.append(f"Kiedy przypłynie {numbers[1]}?")
    if user.role in MATERIAL_ROLES:
        ref = db.scalar(select(Material.ref_code).where(Material.is_active)
                        .order_by(Material.ref_code).limit(1))
        if ref:
            out.append(f"Co to za materiał {ref}?")
    return out[:MAX_EXAMPLES]
