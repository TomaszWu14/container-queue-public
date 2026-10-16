"""Demo: historia procesu każdego kontenera („Przebieg” w zakładce historii) i kontener pokazowy
do prowadzonej „historii jednego kontenera” na ekranie powitalnym (pomysł 1 PO).

seed_demo wpisuje stan końcowy i historię samych statusów; tu dokładamy kroki odprawy, dokumentów
i planu — w czasie zgodnym z etapami (dokumenty w transporcie, odprawa w porcie, plan przy
odprawie), żeby oś czasu czytała się jak prawdziwy proces."""
import datetime as dt

from app.app_settings import set_setting
from app.document_tiles import required
from app.models import Attachment, AuditLog, Container, CustomsStatus, DocumentStatus, PlanningStatus
from app.models.enums import ContainerStatus as S
from app.models.enums import customs_rank
from scripts.seed_demo_process import _gaps

STORY_SETTING = "demo_story_container_id"
_HOUR = dt.timedelta(hours=1)
_CUSTOMS_CHAIN = [s for s in CustomsStatus
                  if s != CustomsStatus.REWIZJA and customs_rank(s) >= customs_rank(CustomsStatus.ZLECONA)]


def _status_times(db, container_id: int) -> dict[str, dt.datetime]:
    rows = db.query(AuditLog).filter_by(entity_type="containers", entity_id=container_id, field="status")
    return {r.new_value: r.created_at for r in rows}


def _customs_steps(status: CustomsStatus) -> list[CustomsStatus]:
    if status == CustomsStatus.REWIZJA:   # rewizja po zgłoszeniu (customs_rank = DRAFT_POTWIERDZONY)
        return [s for s in _CUSTOMS_CHAIN if customs_rank(s) <= customs_rank(status)] + [status]
    return [s for s in _CUSTOMS_CHAIN if customs_rank(s) <= customs_rank(status)]


def _first(times: dict[str, dt.datetime], *statuses: S) -> dt.datetime | None:
    return next((times[s.value] for s in statuses if s.value in times), None)


def history(db, containers: list[Container], agency_name: str, author_id: int) -> int:
    """Wpisy historii kroków procesu (po process/documents w seed_demo). Zwraca liczbę wpisów."""
    db.flush()
    now = dt.datetime.now(dt.UTC).replace(tzinfo=None) - _HOUR
    added = 0

    def add(c: Container, at: dt.datetime | None, field: str, new: str, old: str | None = None,
            note: str = "") -> None:
        nonlocal added
        if at is None:
            return
        db.add(AuditLog(entity_type="containers", entity_id=c.id, field=field, old_value=old,
                        new_value=new, note=note, user_id=author_id, created_at=min(at, now)))
        added += 1

    for i, c in enumerate(containers):
        times = _status_times(db, c.id)
        docs_at = _first(times, S.W_TRANSPORCIE, S.TRANSPORT_WSTEPNY)
        attachments = db.query(Attachment).filter_by(container_id=c.id).order_by(Attachment.id).all()
        for k, a in enumerate(attachments):
            at = _first(times, S.DOSTARCZONY) if a.filename.startswith("CMR") else docs_at
            add(c, at and at + _HOUR * (k + 1), "attachment_upload", a.filename)
        port_at = _first(times, S.W_PORCIE, S.ODPRAWA)
        if c.customs_agency_id and port_at:
            add(c, port_at + _HOUR, "customs_agency", agency_name)
            missing = sorted(required(c) & _gaps(i))
            if c.document_status == DocumentStatus.WYSLANE:
                note = "wysyłka dokumentów do agencji celnej" + (f" MIMO braków: {', '.join(missing)}"
                                                                   if missing else "")
                add(c, port_at + 2 * _HOUR, "document_status", DocumentStatus.WYSLANE.value, note=note)
            for k, step in enumerate(_customs_steps(c.customs_status)):
                add(c, port_at + _HOUR * (3 + 6 * k), "customs_status", step.value)
        plan_at = _first(times, S.ODPRAWA, S.W_PORCIE)
        if plan_at and c.planning_status in (PlanningStatus.WYSLANE, PlanningStatus.POTWIERDZONE):
            add(c, plan_at + 4 * _HOUR, "planning_status", PlanningStatus.WYSLANE.value)
            if c.planning_status == PlanningStatus.POTWIERDZONE:
                add(c, plan_at + 20 * _HOUR, "planning_status", PlanningStatus.POTWIERDZONE.value)
                if c.notify_date:
                    add(c, plan_at + 20 * _HOUR, "notify_date", c.notify_date.isoformat())
    return added


def showcase(db, containers: list[Container]) -> int | None:
    """Kontener pokazowy: dostarczony, z agencją, kompletem dokumentów i potwierdzonym planem —
    cały proces na osi."""
    for i, c in enumerate(containers):
        if (c.status == S.DOSTARCZONY and c.customs_agency_id and not (required(c) & _gaps(i))
                and c.planning_status == PlanningStatus.POTWIERDZONE):
            set_setting(db, STORY_SETTING, str(c.id))
            return c.id
    return None
