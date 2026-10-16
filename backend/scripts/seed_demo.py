"""Instancja portfolio: KASUJE wszystkie dane i załączniki, wgrywa zmyślone dane pokazowe
(dostawcy, kontenery, kierowcy, konta) + konto demo tylko do odczytu.

Bezpieczniki (oba wymagane — na zwykłej instancji skrypt odmawia):
  1. DEMO_READONLY_LOGINS ustawione (tylko instancja pokazowa je ma),
  2. flaga --wyczysc-wszystko.
Uruchom z backend/ (w kontenerze app):
  DEMO_PASSWORD='<min. 12 znaków>' python -m scripts.seed_demo --wyczysc-wszystko
Schemat i alembic_version zostają (czyszczone są wiersze), więc kolejne wdrożenia działają normalnie.
"""
import datetime as dt
import os
import pathlib
import random
import secrets
import sys

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.main import bootstrap  # przez app.main: kolejność importów omija cykl modułów (ARCH-002)
from app.iso6346 import check_digit
from app.models import (AuditLog, Company, Container, CustomsAgency, Forwarder, TrackingEvent, User,
                        Warehouse)
from app.models.enums import ContainerStatus, Role, today_pl
from app.security import hash_password, validate_password_policy
from scripts import seed_demo_process as process
from scripts import seed_demo_story as story

FLAG = "--wyczysc-wszystko"
SUPPLIERS = ["Ningbo Demo Trading Co.", "Qingdao Przykładowe Tekstylia", "Shenzhen Pokazowa Elektronika",
             "Xiamen Wzorcowe Meble", "Dostawca Portugalski Demo Lda", "Foshan Testowe Oświetlenie"]
VESSELS = ["DEMO EXPRESS", "SAMPLE STAR", "PRZYKŁAD MAERSK", "TEST HORIZON"]
# ostatnie zdarzenie trackingu wg etapu — porty z tracking/geo.py, żeby punkt trafił na mapę
TRACK = {ContainerStatus.TRANSPORT_WSTEPNY: ("LOAD", "Załadunek na statek", ["NINGBO", "QINGDAO", "SHENZHEN", "XIAMEN"]),
         ContainerStatus.W_TRANSPORCIE: ("TRANSSHIP", "Przeładunek", ["SINGAPORE", "COLOMBO", "PORT SAID", "PIRAEUS"]),
         ContainerStatus.W_PORCIE: ("DISCHARGE", "Wyładunek w porcie", ["GDANSK", "HAMBURG", "ROTTERDAM"])}


def refuse(msg: str) -> None:
    raise SystemExit(f"seed_demo: ODMOWA — {msg}")


def check_guards(argv: list[str]) -> list[str]:
    demo = [x.strip() for x in settings.demo_readonly_logins.split(",") if x.strip()]
    if not demo:
        refuse("brak DEMO_READONLY_LOGINS — to nie jest instancja pokazowa.")
    if FLAG not in argv:
        refuse(f"brak flagi {FLAG} (skrypt kasuje WSZYSTKIE dane).")
    return demo


def wipe() -> None:
    Base.metadata.create_all(engine)   # idempotentne (jak start aplikacji) — pusta baza też zadziała
    with engine.begin() as conn:   # wiersze, nie schemat — alembic_version zostaje
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    uploads = pathlib.Path(settings.uploads_dir)
    if uploads.is_dir():
        for f in uploads.rglob("*"):
            if f.is_file():
                f.unlink()


def container_no(i: int) -> str:
    prefix = ["MSKU", "TCLU", "CMAU", "HLXU", "MSDU"][i % 5]
    serial = 100000 + i * 13
    while check_digit(f"{prefix}{serial:06d}") == 10:
        serial += 1
    body = f"{prefix}{serial:06d}"
    return body + str(check_digit(body))


def seed(demo_logins: list[str], password: str, n: int = 150) -> int:
    random.seed(2026)
    bootstrap()   # domyślne spółki, słowniki, admin z ADMIN_PASSWORD
    db = SessionLocal()
    acme = db.query(Company).filter_by(code="ACME").one()
    dlt = Warehouse(name="DLT", company_id=acme.id)
    wz = Warehouse(name="ACME", company_id=acme.id)
    agency = CustomsAgency(name="Agencja Celna Demo Sp. z o.o.")
    fw = db.query(Forwarder).first() or Forwarder(name="Spedycja Demo")
    db.add_all([dlt, wz, agency, fw])
    db.flush()
    # US-028: rola wg słowa w loginie (demo-spedytor, demo-agencja, demo-magazyn), domyślnie
    # logistyka (nie admin: bez logów serwera i monitora hosta). Każde konto jest w
    # DEMO_READONLY_LOGINS, więc API odrzuca jego zapisy (security._enforce_demo_readonly).
    for login in demo_logins:
        db.add(User(login=login, hashed_password=hash_password(password), email=f"{login}@example.com",
                    **process.account_fields(login, acme.id, fw.id, agency.id, dlt.id)))
    # autor historii zmian — fikcyjna, nieaktywna (nie zaloguje się), hasło losowe i nieznane
    author = User(login="m.przykladowa", full_name="Marta Przykładowa", role=Role.logistics,
                  company_id=acme.id, email="m.przykladowa@example.com", is_active=False,
                  hashed_password=hash_password(secrets.token_urlsafe(24)))
    db.add(author)
    db.flush()
    statuses, today = list(ContainerStatus), today_pl()
    ctx = process.dictionaries(db)
    containers: list[Container] = []
    # ETA zagęszczone wokół dziś (domyślny widok kolejki = bieżący tydzień nie może świecić
    # pustką); status wg ETA w kolejności procesu: najpóźniejsze ZAPOWIEDZIANY, minione zrealizowane
    offsets = sorted((round(random.triangular(-45, 45, -10)) for _ in range(n)), reverse=True)
    for i, offset in enumerate(offsets):
        eta = today + dt.timedelta(days=offset)
        driver = i % 4 == 0
        status = statuses[i * len(statuses) // n]
        track = TRACK.get(status)
        container = Container(
            container_no=container_no(i), company_id=acme.id, status=status,
            rf_number=f"RF-DEMO-{i:04d}" if track else "",
            warehouse_id=[dlt.id, wz.id, None][i % 3], supplier_raw=SUPPLIERS[i % len(SUPPLIERS)],
            vessel=VESSELS[i % len(VESSELS)], eta=eta, notify_date=eta + dt.timedelta(days=5) if i % 3 else None,
            forwarder_id=fw.id if i % 2 == 0 else None, customs_agency_id=agency.id if i % 5 == 0 else None,
            # zmyślone dane kierowcy: numer 000 nie istnieje w polskiej numeracji
            driver_name=f"Kierowca Demo {i}" if driver else "",
            driver_phone=f"+48 000 000 {i:03d}" if driver else "",
            truck_no=f"DEMO{i:03d}" if driver else "",
        )
        db.add(container)
        db.flush()
        containers.append(container)
        _history(db, container, statuses, author, today)
        if track:   # mapa śledzenia pokazuje kontenery z RF i ostatnim faktycznym zdarzeniem
            code, desc, ports = track
            db.add(TrackingEvent(container_id=container.id, event_code=code, description=desc,
                                 location=ports[i % len(ports)], vessel=container.vessel,
                                 occurred_at=dt.datetime.combine(today, dt.time(8)) - dt.timedelta(days=1 + i % 5),
                                 source="demo"))
    # US-027: cały proces, nie tylko kolejka — odprawa, demurrage, zamówienia, dokumenty, awizacje
    process.process(db, containers, agency.id, ctx, today)
    process.orders(db, containers, acme.id, ctx)
    process.documents(db, containers, ctx, author.id)
    process.avizo(db, containers, acme.id, fw.id, author.id)
    # pomysł 1 i 3 PO: kroki procesu na osi „Przebieg” + kontener pokazowy na ekranie powitalnym
    story.history(db, containers, agency.name, author.id)
    story.showcase(db, containers)
    db.commit()
    count = db.query(Container).count()
    db.close()
    return count


def _history(db, container: Container, statuses: list, author: User, today: dt.date) -> None:
    """Historia kontenera: utworzenie + kolejne zmiany statusu do bieżącego (rosnące daty)."""
    reached = statuses.index(container.status)
    start = dt.datetime.combine(min(container.eta, today) - dt.timedelta(days=50), dt.time(9))
    end = dt.datetime.combine(min(container.eta + dt.timedelta(days=5), today), dt.time(15))
    step = (end - start) / (reached + 1)
    rows = [("created", None, container.container_no)] + [
        ("status", statuses[k - 1].value, statuses[k].value) for k in range(1, reached + 1)]
    for k, (field, old, new) in enumerate(rows):
        at = start + step * k   # dzień z osi czasu, godzina w czasie pracy biura (8–16)
        db.add(AuditLog(entity_type="containers", entity_id=container.id, field=field,
                        old_value=old, new_value=new, user_id=author.id,
                        created_at=at.replace(hour=8 + (container.id + k) % 9, minute=(k * 17) % 60,
                                              second=0, microsecond=0)))


def main(argv: list[str]) -> None:
    demo = check_guards(argv)
    password = os.environ.get("DEMO_PASSWORD", "")
    validate_password_policy(password)
    wipe()
    print(f"seed_demo: gotowe — {seed(demo, password)} kontenerów, konta demo: {', '.join(demo)}")


if __name__ == "__main__":
    main(sys.argv[1:])
