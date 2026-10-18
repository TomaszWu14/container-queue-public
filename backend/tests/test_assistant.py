"""Asystent wiedzy (#38 plaster 2): fakty z bazy z izolacją + lokalny model (Ollama)."""
from sqlalchemy import select

from app import llm
from app.config import settings
from app.models import Company, Container, Forwarder, Material, Role, User
from app.security import create_access_token

from .conftest import login


def _seed(db):
    co = db.scalars(select(Company)).first()
    db.add(Container(company_id=co.id, container_no="MSCU1234567", vessel="MV DEMO BOREAS"))
    db.add(Material(ref_code="NL753-S-40", ref_norm="NL753S40", name_pl="Cewnik Nelaton",
                    ean="5901234567890"))
    db.commit()
    return co


def test_facts_without_model(client, db_session, monkeypatch):
    _seed(db_session)
    monkeypatch.setattr(settings, "ollama_url", "")
    r = client.post("/api/assistant/ask", headers=login(client),
                    json={"question": "Gdzie jest MSCU 1234567 i co to NL753-S-40?"}).json()
    assert r["ai"] is False and r["answer_source"] == "template"   # US-039: szablon zamiast modelu
    assert "Kontener MSCU1234567" in r["answer"] and "statek MV DEMO BOREAS" in r["answer"]
    assert "Materiał NL753-S-40: Cewnik Nelaton" in r["answer"]
    assert r["facts"]["kontenery"][0]["statek"] == "MV DEMO BOREAS"
    assert r["facts"]["materialy"][0]["nazwa_pl"] == "Cewnik Nelaton"
    by_name = client.post("/api/assistant/ask", headers=login(client),
                          json={"question": "jaki jest cewnik?"}).json()
    assert by_name["facts"]["materialy"][0]["ref"] == "NL753-S-40"


def test_model_answers_from_facts_and_failure_keeps_facts(client, db_session, monkeypatch):
    _seed(db_session)
    monkeypatch.setattr(settings, "ollama_url", "http://ollama:11434")
    seen = {}
    monkeypatch.setattr(llm, "chat", lambda model, prompt, system="", purpose="": seen.update(
        model=model, prompt=prompt, purpose=purpose) or "Kontener płynie statkiem MV DEMO BOREAS.")
    r = client.post("/api/assistant/ask", headers=login(client),
                    json={"question": "status MSCU1234567"}).json()
    assert r["answer"] == "Kontener płynie statkiem MV DEMO BOREAS." and r["ai"] is True
    assert r["answer_source"] == "ai"
    assert seen["model"] == settings.assistant_model and "MV DEMO BOREAS" in seen["prompt"]
    assert seen["purpose"] == "assistant"     # AI-004: etykieta metryki wywołania

    def boom(*a, **k):
        raise TimeoutError
    monkeypatch.setattr(llm, "chat", boom)
    r = client.post("/api/assistant/ask", headers=login(client),
                    json={"question": "status MSCU1234567"}).json()
    assert r["answer_source"] == "template" and r["facts"]["kontenery"]   # awaria modelu → szablon


def test_no_facts_means_no_model_call(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "ollama_url", "http://ollama:11434")
    monkeypatch.setattr(llm, "chat", lambda *a, **k: (_ for _ in ()).throw(AssertionError))
    r = client.post("/api/assistant/ask", headers=login(client), json={"question": "hej"}).json()
    assert r["answer"] is None and r["answer_source"] is None
    assert r["facts"] == {"kontenery": [], "materialy": []}


def test_isolation_forwarder_sees_neither_foreign_container_nor_materials(client, db_session):
    _seed(db_session)
    fw = Forwarder(name="Obcy spedytor")
    db_session.add(fw)
    db_session.flush()
    u = User(login="fw-a", hashed_password="x", role=Role.forwarder, forwarder_id=fw.id)
    db_session.add(u)
    db_session.commit()
    hdr = {"Authorization": f"Bearer {create_access_token(u)}"}
    r = client.post("/api/assistant/ask", headers=hdr,
                    json={"question": "MSCU1234567 NL753-S-40"}).json()
    assert r["facts"] == {"kontenery": [], "materialy": []}


def test_facts_mask_supplier_like_rest_of_app(client, db_session):
    """Audyt AI-001: fakty asystenta idą przez hidden_fields — magazyn i agencja celna nie widzą
    dostawcy (jak w to_out/karcie kontenera), logistyka widzi."""
    from app.models import CustomsAgency, Supplier, Warehouse
    co = _seed(db_session)
    sup = Supplier(name="Tajny Dostawca Sp. z o.o.")
    wh = Warehouse(company_id=co.id, name="MAG-A")
    ag = CustomsAgency(name="Agencja A")
    db_session.add_all([sup, wh, ag])
    db_session.flush()
    c = db_session.scalars(select(Container).where(Container.container_no == "MSCU1234567")).one()
    c.supplier_id, c.warehouse_id, c.customs_agency_id = sup.id, wh.id, ag.id
    users = {
        "warehouse": User(login="mag-a", hashed_password="x", role=Role.warehouse,
                          company_id=co.id, warehouse_id=wh.id),
        "customs": User(login="agencja-a", hashed_password="x", role=Role.customs,
                        customs_agency_id=ag.id),
        "logistics": User(login="log-a", hashed_password="x", role=Role.logistics, company_id=co.id),
    }
    db_session.add_all(users.values())
    db_session.commit()
    for role, u in users.items():
        hdr = {"Authorization": f"Bearer {create_access_token(u)}"}
        facts = client.post("/api/assistant/ask", headers=hdr,
                            json={"question": "Gdzie jest MSCU1234567?"}).json()["facts"]["kontenery"]
        assert len(facts) == 1, role
        if role == "logistics":
            assert facts[0]["dostawca"] == "Tajny Dostawca Sp. z o.o."
        else:
            assert "dostawca" not in facts[0], role
            assert facts[0]["statek"] == "MV DEMO BOREAS", role   # dane operacyjne zostają


def test_fact_fields_exist_in_container_out():
    # literówka w mapowaniu = pole po cichu niemaskowane
    from app.routers.assistant import _FACT_FIELD
    from app.schemas import ContainerOut
    assert set(_FACT_FIELD.values()) <= set(ContainerOut.model_fields)


def test_template_sentence_fields():
    from app import assistant_template as T
    text = T.answer({"kontenery": [{"kontener": "ABCU1234567", "status": "ODPRAWA", "eta": "2026-10-20",
                                    "awizacja": None, "odprawa": "ZLECONA"}], "materialy": []})
    assert text == ("Kontener ABCU1234567, etap 8 · Odprawa celna, ETA 2026-10-20, bez awizacji, "
                    "odprawa: zlecona agencji.")
    assert T.answer({"kontenery": [], "materialy": []}) is None


def test_examples_scoped_and_answerable(client, db_session, monkeypatch):
    from app.database import SessionLocal
    from app.security import hash_password
    monkeypatch.setattr(settings, "ollama_url", "")
    with SessionLocal() as db:
        own = Company(name="Asyst A", code="ASA")
        other = Company(name="Asyst B", code="ASB")
        db.add_all([own, other])
        db.flush()
        db.add_all([Container(company_id=own.id, container_no="ASXU1000001"),
                    Container(company_id=other.id, container_no="ASXU2000002"),
                    User(login="as-lg", hashed_password=hash_password("pass12345"), role=Role.logistics,
                         company_id=own.id)])
        db.commit()
    headers = login(client, "as-lg", "pass12345")
    qs = client.get("/api/assistant/examples", headers=headers).json()["questions"]
    assert qs[0] == "Jaki jest status ASXU1000001?"            # tylko kontenery swojej spółki
    assert not any("ASXU2000002" in q for q in qs) and len(qs) <= 3
    r = client.post("/api/assistant/ask", headers=headers, json={"question": qs[0]}).json()
    assert r["answer_source"] == "template" and "ASXU1000001" in r["answer"]
