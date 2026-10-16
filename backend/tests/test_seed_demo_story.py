"""Pomysł 1 i 3 PO: demo ma kontener pokazowy z pełnym procesem na osi „Przebieg” (statusy, dokumenty,
agencja, przekazanie dokumentów, odprawa, plan), w kolejności zgodnej z etapami; ekran powitalny
dostaje jego numer z brandingu tylko na instancji demo."""
from app.config import settings
from app.database import SessionLocal
from app.models import AuditLog, Container
from app.models.enums import ContainerStatus as S
from tests.test_seed_demo_process import seeded  # noqa: F401 — fixture

from .conftest import login


def _story(db, cid):
    rows = (db.query(AuditLog).filter_by(entity_type="containers", entity_id=cid)
            .order_by(AuditLog.created_at, AuditLog.id).all())
    return [(r.field, r.new_value) for r in rows]


def test_showcase_container_tells_the_whole_process(seeded, client):  # noqa: F811
    branding = client.get("/api/public/branding").json()
    cid = branding["demo_story_container_id"]
    assert isinstance(cid, int)
    with SessionLocal() as db:
        assert db.get(Container, cid).status == S.DOSTARCZONY
        story = _story(db, cid)
    fields = [f for f, _ in story]
    for needed in ("attachment_upload", "customs_agency", "document_status", "customs_status",
                   "planning_status", "notify_date"):
        assert needed in fields, needed
    # kolejność procesu: dokumenty przed odprawą, agencja przed przekazaniem dokumentów, plan po odprawie
    def first(field, value=None):
        return next(i for i, (f, v) in enumerate(story) if f == field and (value is None or v == value))
    assert first("status", "W_PORCIE") < first("customs_agency") < first("document_status")
    assert first("attachment_upload") < first("customs_agency")
    assert first("planning_status", "WYSLANE") < first("planning_status", "POTWIERDZONE")
    # „Przebieg” widzi te kroki przez zwykłe API historii
    history = client.get(f"/api/containers/{cid}/history", headers=login(client, "demo", "Demo-Portfolio-2026"))
    assert history.status_code == 200 and len(history.json()) == len(story)


def test_branding_has_no_story_outside_demo(client, monkeypatch):
    monkeypatch.setattr(settings, "demo_readonly_logins", "")
    assert client.get("/api/public/branding").json()["demo_story_container_id"] is None


def test_demo_value_panel_shows_demurrage_warnings(seeded, client):  # noqa: F811
    hdr = login(client, "demo", "Demo-Portfolio-2026")
    risks = client.get("/api/stats/demurrage-risk?limit=100", headers=hdr).json()
    value = client.get("/api/stats/value", headers=hdr).json()
    assert risks and value["demurrage_warned"] == len(risks)
