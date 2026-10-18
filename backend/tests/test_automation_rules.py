"""US-036: kreator reguł bez kodu — zamknięty katalog warunków, zapis tylko admin z audytem,
podgląd w zakresie użytkownika, pętla tła wysyła jedno powiadomienie na regułę/kontener/dzień."""
import datetime as dt

from app import automation_rules as R
from app.database import SessionLocal
from app.models import AuditLog, Company, Container, Notification, Role, User, today_pl, utcnow
from app.models.enums import ContainerStatus as S
from app.security import hash_password

from .conftest import login

TODAY = today_pl()


def _user(login_name, role, company_id=None):
    with SessionLocal() as db:
        db.add(User(login=login_name, hashed_password=hash_password("pass12345"), role=role,
                    company_id=company_id))
        db.commit()


def _companies():
    with SessionLocal() as db:
        return [c.id for c in db.query(Company).order_by(Company.id).limit(2)]


def _container(no, company_id, **fields):
    with SessionLocal() as db:
        c = Container(container_no=no, company_id=company_id, **fields)
        db.add(c)
        db.commit()
        return c.id


def _rule(**kw):
    base = {"name": "Brak kierowcy", "condition": "no_driver", "days": 2}
    return {**base, **kw}


def test_conditions_match_expected_containers():
    a, _ = _companies()
    eta_late = _container("RULU1000001", a, status=S.W_PORCIE, eta=TODAY - dt.timedelta(days=5))
    _container("RULU1000002", a, status=S.DOSTARCZONY, eta=TODAY - dt.timedelta(days=5))   # dostarczony
    soon_early = _container("RULU1000003", a, status=S.W_TRANSPORCIE, notify_date=TODAY + dt.timedelta(days=1),
                            driver_name="Jan")
    no_driver = _container("RULU1000004", a, status=S.AWIZOWANY, notify_date=TODAY + dt.timedelta(days=2))
    _container("RULU1000005", a, status=S.AWIZOWANY, notify_date=TODAY + dt.timedelta(days=9))     # za daleko
    plan = _container("RULU1000006", a, status=S.W_PORCIE, planning_sent_at=utcnow() - dt.timedelta(days=4))
    with SessionLocal() as db:
        def ids(**kw):
            return {c.id for c in R.matching(db, R.Rule(name="x", **kw), today=TODAY)
                    if c.container_no.startswith("RULU")}
        assert ids(condition="eta_passed", days=3) == {eta_late}
        assert ids(condition="notify_soon_status", days=2, status="ODPRAWA") == {soon_early}
        assert ids(condition="no_driver", days=2) == {no_driver}
        assert ids(condition="plan_unconfirmed", days=3) == {plan}
        assert ids(condition="plan_unconfirmed", days=5) == set()


def test_save_validates_and_audits(client, admin_headers):
    bad = client.put("/api/automations/rules", headers=admin_headers,
                     json={"rules": [_rule(condition="notify_soon_status")]})   # bez statusu
    assert bad.status_code == 422
    assert client.put("/api/automations/rules", headers=admin_headers,
                      json={"rules": [_rule(days=61)]}).status_code == 422
    assert client.put("/api/automations/rules", headers=admin_headers,
                      json={"rules": [_rule(condition="usun_wszystko")]}).status_code == 422
    r = client.put("/api/automations/rules", headers=admin_headers, json={"rules": [_rule()]})
    assert r.status_code == 200
    rule = r.json()["rules"][0]
    assert len(rule["id"]) == 12 and rule["enabled"] is True
    client.put("/api/automations/rules", headers=admin_headers,
               json={"rules": [{**rule, "days": 3}]})
    client.put("/api/automations/rules", headers=admin_headers, json={"rules": []})
    with SessionLocal() as db:
        rows = db.query(AuditLog).filter(AuditLog.entity_type == "automation_rule").order_by(AuditLog.id).all()
        assert [(a.old_value is None, a.new_value is None) for a in rows] == [
            (True, False), (False, False), (False, True)]          # dodana, zmieniona, usunięta
    too_many = [_rule(name=f"r{i}") for i in range(R.MAX_RULES + 1)]
    assert client.put("/api/automations/rules", headers=admin_headers,
                      json={"rules": too_many}).status_code == 422


def test_only_admin_saves(client):
    _user("logi-rule", Role.logistics, _companies()[0])
    headers = login(client, "logi-rule", "pass12345")
    assert client.get("/api/automations/rules", headers=headers).status_code == 200
    assert client.put("/api/automations/rules", headers=headers,
                      json={"rules": [_rule()]}).status_code == 403


def test_preview_scoped_to_user_companies(client, admin_headers):
    a, b = _companies()
    _container("RULU2000001", a, status=S.AWIZOWANY, notify_date=TODAY + dt.timedelta(days=1))
    _container("RULU2000002", b, status=S.AWIZOWANY, notify_date=TODAY + dt.timedelta(days=1))
    _user("logi-prev", Role.logistics, a)
    params = {"condition": "no_driver", "days": 2}
    mine = client.get("/api/automations/rules/preview", params=params,
                      headers=login(client, "logi-prev", "pass12345")).json()
    everyone = client.get("/api/automations/rules/preview", params=params, headers=admin_headers).json()
    nos = lambda body: {s["container_no"] for s in body["sample"]}   # noqa: E731
    assert "RULU2000002" not in nos(mine) and "RULU2000001" in nos(mine)
    assert {"RULU2000001", "RULU2000002"} <= nos(everyone) and everyone["count"] > mine["count"]
    assert client.get("/api/automations/rules/preview", headers=admin_headers,
                      params={"condition": "notify_soon_status", "days": 2}).status_code == 422


def test_run_rules_notifies_once_per_day_and_respects_switches(client, admin_headers):
    a, _ = _companies()
    cid = _container("RULU3000001", a, status=S.AWIZOWANY, notify_date=TODAY + dt.timedelta(days=1))
    _user("logi-run", Role.logistics, a)
    client.put("/api/automations/rules", headers=admin_headers, json={"rules": [
        _rule(), _rule(name="Wyłączona", enabled=False), _rule(name="Do adminów", notify="admins")]})
    with SessionLocal() as db:
        assert R.run_rules(db, today=TODAY) > 0
        first = db.query(Notification).filter_by(container_id=cid, kind="rule").count()
        R.run_rules(db, today=TODAY)                                      # drugi przebieg tego dnia
        assert db.query(Notification).filter_by(container_id=cid, kind="rule").count() == first
        titles = {n.title for n in db.query(Notification).filter_by(container_id=cid, kind="rule")}
        assert titles == {"Reguła „Brak kierowcy”: RULU3000001", "Reguła „Do adminów”: RULU3000001"}
        logi = db.query(User).filter_by(login="logi-run").one()
        mine = {n.title for n in db.query(Notification).filter_by(user_id=logi.id, kind="rule")}
        assert mine == {"Reguła „Brak kierowcy”: RULU3000001"}            # „Do adminów” nie do logistyki


def test_broken_setting_does_not_stop_other_rules():
    with SessionLocal() as db:
        from app import app_settings
        app_settings.set_setting(db, R.SETTING_KEY,
                                 '[{"name": "ok", "condition": "no_driver", "days": 1}, {"name": "zły"}]')
        db.commit()
        assert [r.name for r in R.load(db)] == ["ok"]


def test_rule_channels_choose_where_alert_goes(client, admin_headers, monkeypatch):
    """US-063: reguła wybiera kanały — tu tylko zdarzenie do n8n: bez e-maila i Teams, rekord przeczytany
    (ślad dla deduplikacji); pusty wybór kanałów odrzucony."""
    from app import notifications
    sent: list[str] = []
    monkeypatch.setattr(notifications, "_send_email", lambda r, *a: sent.append("email") if r else None)
    monkeypatch.setattr(notifications, "_send_teams", lambda *a: sent.append("teams"))
    monkeypatch.setattr(notifications, "send_automation_event", lambda *a, **k: sent.append("n8n"))
    a, _ = _companies()
    cid = _container("RULU3000002", a, status=S.AWIZOWANY, notify_date=TODAY + dt.timedelta(days=1))
    with SessionLocal() as db:
        db.query(User).filter_by(login="admin").update({"email": "admin@example.com"})
        db.commit()
    r = client.put("/api/automations/rules", headers=admin_headers, json={"rules": [
        _rule(name="Tylko n8n", notify="admins", channels=["n8n", "n8n"])]})
    assert r.status_code == 200 and r.json()["rules"][0]["channels"] == ["n8n"]
    assert r.json()["channels"] == ["bell", "email", "teams", "n8n"]
    with SessionLocal() as db:
        assert R.run_rules(db, today=TODAY) > 0
        rows = db.query(Notification).filter_by(container_id=cid, kind="rule").all()
        assert rows and all(n.is_read for n in rows)
    assert sent == ["n8n"]
    assert R.Rule.model_validate(_rule()).channels == ["bell", "email", "teams", "n8n"]   # domyślnie wszystkie
    r = client.put("/api/automations/rules", headers=admin_headers, json={"rules": [_rule(channels=[])]})
    assert r.status_code == 422
