"""US-017 (P-09): „Wyślij plan do spedycji” wysyła spedytorowi maila z proponowanymi datami.

Decyzje PO 2026-10-16: plan idzie wcześniej niż awizacja i zawiera same daty; spedytor odpowiada,
logując się do aplikacji (zakładka Spedycja — plany czekające na potwierdzenie), bez nowych linków
publicznych. Jeden mail na (spedytor, spółka), jak przy awizacji — separacja spółek. Bez danych
dostawcy (spedytor nie widzi ich także w formularzu awizacji)."""
import logging

from sqlalchemy.orm import Session

from .audit import record
from .config import settings
from .html_templates import render
from .mail_html import table_context
from .models import Container, User
from .notifications import send_html_email

logger = logging.getLogger(__name__)

COLUMNS = ["unload", "container", "eta", "vessel", "warehouse"]


def plan_subject(containers: list[Container]) -> str:
    company = containers[0].company.name if containers[0].company else ""
    return (f"Propozycja dat dostaw / Proposed delivery dates — {len(containers)} kont."
            + (f" — {company}" if company else ""))


def plan_html(containers: list[Container], operator: User, base: str) -> str:
    ordered = sorted(containers, key=lambda c: (c.notify_date is None, c.notify_date, c.id))
    return render("mail/plan_proposal.html", link=f"{base}/spedycja",
                  operator=operator.full_name or operator.login,
                  **table_context(ordered, COLUMNS))


def send_plan_mails(db: Session, containers: list[Container], user: User, base: str) -> dict:
    """Maile do spedytorów dla kontenerów, którym właśnie wysłano plan. Błąd jednego maila nie
    przerywa pozostałych; brak SMTP = jawny błąd w `failed` (status planu zostaje — spedytor
    z kontem widzi plan w aplikacji). Commit należy do wołającego."""
    groups: dict[tuple[int | None, int], list[Container]] = {}
    for c in containers:
        groups.setdefault((c.forwarder_id, c.company_id), []).append(c)
    emailed: list[dict] = []
    missing_email: list[str] = []
    failed: list[dict] = []
    for items in groups.values():
        forwarder = items[0].forwarder
        if forwarder is None:   # wołający przekazuje tylko kontenery ze spedytorem
            continue
        if not forwarder.email:
            missing_email.append(forwarder.name)
            continue
        try:
            send_html_email([forwarder.email], plan_subject(items), plan_html(items, user, base),
                            reply_to=user.email or settings.smtp_from)
        except Exception as exc:  # noqa: BLE001 — nie przerywamy pozostałych wysyłek
            logger.warning("plan: mail do spedytora %s nie wyszedł", forwarder.name, exc_info=True)
            failed.append({"forwarder": forwarder.name, "error": str(exc)})
            continue
        for c in items:
            record(db, entity_type="containers", entity_id=c.id, field="plan_mail", old_value=None,
                   new_value=forwarder.email, user=user, note=f"mail z planem do {forwarder.name}")
        emailed.append({"forwarder": forwarder.name, "email": forwarder.email, "containers": len(items)})
    return {"emailed": emailed, "missing_email": missing_email, "failed": failed}
