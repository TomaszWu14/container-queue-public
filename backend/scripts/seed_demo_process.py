"""Dane demo pokazujące cały proces, nie tylko kolejkę (US-027, US-028).

Wywoływane z scripts/seed_demo.py po utworzeniu kontenerów. Wszystko zmyślone: armatorzy,
porty docelowe, zamówienia, dokumenty (małe PDF-y z tekstem „DEMO”), awizacje. Reguły jak
w aplikacji: status odprawy zgodny z etapem kontenera, wymagane kafelki wg document_tiles,
termin demurrage wg notification_alerts (przybycie + dni wolne)."""
import datetime as dt
import hashlib
import pathlib
import secrets

from app.config import settings
from app.document_tiles import required
from app.models import (Attachment, AvizoFormToken, AvizoItem, AvizoRequest, AvizoStatus, Carrier,
                        Container, CustomsStatus, DeliveryConfirmation, DocumentStatus, DocumentType,
                        Order, PlanningStatus, Port, PortCategory, Role, TransportType, customs_rank,
                        utcnow)
from app.models.enums import ContainerStatus as S

# kody kafelków jak w migracji tile001 + typy bazowe; CMR bez kafelka (widzi go spedytor)
DOC_TYPES = (("PI", "Faktura proforma (PI)"), ("CI", "Faktura handlowa (CI)"),
             ("PL", "Packing list (PL)"), ("BL", "Konosament (B/L)"), ("SAD_DRAFT", "Draft SAD"),
             ("SAD_PZ", "SAD — po odprawie (PZ)"), ("SAD_PW", "SAD — zwolnienie (PW)"), (None, "CMR"))
CARRIERS = (("Demo Ocean Line", 7), ("Przykładowa Żegluga", 10), ("Sample Container Lines", 5))
DEST_PORTS = (("Gdańsk", "PL"), ("Hamburg", "DE"), ("Rotterdam", "NL"))
_PORT_MIX = (0, 0, 0, 1, 1, 2)   # Gdańsk ½, Hamburg ⅓, Rotterdam ⅙
REWIZJA_NOTE = "Kontrola fizyczna: weryfikacja kodu CN i wagi, czekamy na protokół (dane demo)."
# rola konta demo wg słowa w loginie; konto MUSI być w DEMO_READONLY_LOGINS (tylko odczyt)
ROLE_WORDS = ((("spedytor", "forwarder"), Role.forwarder), (("agencja", "celn", "customs"), Role.customs),
              (("magazyn", "warehouse"), Role.warehouse))


def account_fields(login: str, company_id: int, forwarder_id: int, agency_id: int,
                   warehouse_id: int) -> dict:
    """Pola konta demo per rola: partner bez spółki (deps.own_company_id), magazyn zawężony
    do magazynu DLT, reszta = logistyka grupy (widzi wszystkie spółki)."""
    low = login.lower()
    role = next((r for words, r in ROLE_WORDS if any(w in low for w in words)), Role.logistics)
    if role == Role.forwarder:
        return {"role": role, "forwarder_id": forwarder_id, "full_name": "Demo — spedytor"}
    if role == Role.customs:
        return {"role": role, "customs_agency_id": agency_id, "full_name": "Demo — agencja celna"}
    if role == Role.warehouse:
        return {"role": role, "company_id": company_id, "warehouse_id": warehouse_id,
                "full_name": "Demo — magazyn"}
    return {"role": role, "company_id": company_id, "view_all_companies": True,
            "full_name": "Konto demo"}


def dictionaries(db) -> dict:
    """Typy dokumentów (seed_demo czyści też słowniki z migracji), armatorzy, porty docelowe."""
    types = {}
    for i, (code, name) in enumerate(DOC_TYPES):
        types[code or name] = DocumentType(name=name, tile_code=code, sort_order=(i + 1) * 10)
    carriers = [Carrier(name=n, demurrage_free_days=d) for n, d in CARRIERS]
    ports = [db.query(Port).filter_by(name=n).one_or_none()
             or Port(name=n, country=c, category=PortCategory.OUT) for n, c in DEST_PORTS]
    db.add_all([*types.values(), *carriers, *ports])
    db.flush()
    origin = db.query(Port).filter_by(category=PortCategory.GLOWNY_CN).order_by(Port.id).all()
    return {"types": types, "carriers": carriers, "ports": ports, "origin": origin}


def _customs(status: S, i: int) -> CustomsStatus:
    if status in (S.ZAPOWIEDZIANY, S.W_PRODUKCJI, S.TRANSPORT_WSTEPNY):
        return CustomsStatus.BRAK
    return {S.W_TRANSPORCIE: CustomsStatus.DOKUMENTY_KOMPLETNE if i % 2 else CustomsStatus.BRAK,
            S.W_PORCIE: CustomsStatus.ZLECONA if i % 2 else CustomsStatus.DRAFT_WYSLANY,
            S.ODPRAWA: CustomsStatus.REWIZJA if i % 4 == 0 else CustomsStatus.DRAFT_POTWIERDZONY,
            S.AWIZOWANY: CustomsStatus.ZWOLNIONY if i % 2 else CustomsStatus.ODPRAWIONY,
            S.ZREALIZOWANY: CustomsStatus.ROZLICZONY}.get(status, CustomsStatus.ZWOLNIONY)


def _planning(c: Container, i: int, now: dt.datetime) -> None:
    if not c.notify_date:
        return
    if c.status in (S.AWIZOWANY, S.W_DOSTAWIE, S.DOSTARCZONY, S.ZREALIZOWANY):
        c.planning_status, c.planning_confirmed_at = PlanningStatus.POTWIERDZONE, now
        c.planning_sent_at = now - dt.timedelta(days=2)
    elif c.status in (S.W_PORCIE, S.ODPRAWA) and i % 2:
        c.planning_status, c.planning_sent_at = PlanningStatus.WYSLANE, now - dt.timedelta(days=1)


def _arrival(c: Container, i: int, today: dt.date) -> dt.date | None:
    """Jak notification_alerts: wyładunek z trackingu (seed_demo: dziś − 1 − i % 5), inaczej ETA."""
    if c.status == S.W_PORCIE:
        return today - dt.timedelta(days=1 + i % 5)
    return c.eta if c.eta and c.eta <= today else None


def process(db, containers: list[Container], agency_id: int, ctx: dict, today: dt.date) -> None:
    """Odprawa, porty, armator, demurrage, plan dostawy i ETD — spójnie z etapem kontenera."""
    now = utcnow()
    for i, c in enumerate(containers):
        c.customs_status = _customs(c.status, i)
        assigned = customs_rank(c.customs_status) >= customs_rank(CustomsStatus.ZLECONA)
        c.customs_agency_id = agency_id if assigned else None
        c.customs_assigned_at = now - dt.timedelta(days=4) if assigned else None
        if c.customs_status == CustomsStatus.REWIZJA:
            c.customs_note, c.customs_date = REWIZJA_NOTE, today - dt.timedelta(days=1)
        if c.status in (S.AWIZOWANY, S.W_DOSTAWIE) and not c.notify_date:
            c.notify_date = c.eta + dt.timedelta(days=5)   # awizowany = ma datę dostawy
        _planning(c, i, now)
        c.carrier_id = ctx["carriers"][i % len(ctx["carriers"])].id
        # nierówny podział portów i transportu — wykresy kołowe pulpitu pokazują realną strukturę
        c.port_id = ctx["ports"][_PORT_MIX[i % len(_PORT_MIX)] % len(ctx["ports"])].id
        c.transport_type = TransportType.lotniczy if i % 17 == 0 else (
            TransportType.kolej if i % 4 == 0 else TransportType.morski)
        if c.status != S.ZAPOWIEDZIANY:
            c.etd = c.eta - dt.timedelta(days=35)
        arrival = _arrival(c, i, today)
        if c.status in (S.W_PORCIE, S.ODPRAWA, S.AWIZOWANY) and i % 3 == 0 and arrival:
            c.demurrage_free_days = (today - arrival).days + 2   # termin za 2 dni → alert ≤ 3 dni


def orders(db, containers: list[Container], company_id: int, ctx: dict, size: int = 3,
           count: int = 30) -> None:
    """Zamówienia po `size` kontenerów (sąsiednie ETA = jedna wysyłka dostawcy)."""
    for k in range(count):
        group = containers[k * size:(k + 1) * size]
        if not group:
            break
        origin = ctx["origin"][k % len(ctx["origin"])] if ctx["origin"] else None
        order = Order(number=f"PO-DEMO-2026-{k + 1:03d}", company_id=company_id,
                      container_count=len(group), goods_type="Towar demo (dane zmyślone)",
                      departure_port_id=origin.id if origin else None,
                      readiness_date=min(c.eta for c in group) - dt.timedelta(days=40))
        db.add(order)
        db.flush()
        for c in group:
            c.order_id = order.id


def _pdf(text: str) -> bytes:
    """Najmniejszy poprawny PDF z jedną linią tekstu (bez zależności, do podglądu w panelu)."""
    stream = f"BT /F1 14 Tf 60 760 Td ({text}) Tj ET".encode("latin-1", "replace")
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
            b"/Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for n, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % n + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


def _gaps(i: int) -> set[str]:
    """Celowe braki — kafelki i ostrzeżenia mają co pokazać."""
    return ({"BL"} if i % 7 == 0 else set()) | ({"CI"} if i % 11 == 0 else set())


def documents(db, containers: list[Container], ctx: dict, author_id: int) -> int:
    """Pliki wymaganych kafelków (minus celowe braki) + CMR po rozładunku; status obiegu."""
    uploads = pathlib.Path(settings.uploads_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    count = 0
    for i, c in enumerate(containers):
        codes = sorted(required(c) - _gaps(i))
        if c.status in (S.DOSTARCZONY, S.ZREALIZOWANY):
            codes.append("CMR")
        for code in codes:
            content = _pdf(f"DEMO {code} {c.container_no} - dokument zmyslony, dane pokazowe")
            name = f"{code}_{c.container_no}.pdf"
            stored = f"{c.id}_{secrets.token_hex(8)}_{name}"
            (uploads / stored).write_bytes(content)
            db.add(Attachment(container_id=c.id, filename=name, stored_name=stored,
                              content_type="application/pdf", size=len(content),
                              sha256=hashlib.sha256(content).hexdigest(), uploaded_by_id=author_id,
                              document_type_id=ctx["types"][code].id))
            count += 1
        sent = customs_rank(c.customs_status) >= customs_rank(CustomsStatus.ZLECONA)
        c.document_status = (DocumentStatus.WYSLANE if sent else
                             DocumentStatus.ZALACZONE if codes else DocumentStatus.BRAK)
    return count


def _request(db, company_id, forwarder_id, author_id, status, items, now, **extra) -> AvizoRequest:
    req = AvizoRequest(token=secrets.token_hex(16), company_id=company_id, forwarder_id=forwarder_id,
                       created_by_id=author_id, status=status, language="pl",
                       expires_at=now + dt.timedelta(days=7), **extra)
    db.add(req)
    db.flush()
    confirmed = status not in (AvizoStatus.SENT_STAGE1, AvizoStatus.REJECTED)
    for c in items:
        db.add(AvizoItem(request_id=req.id, container_id=c.id, confirmed=confirmed))
    stage = {AvizoStatus.SENT_STAGE1: 1, AvizoStatus.SENT_STAGE2: 2}.get(status)
    if stage:   # link „czeka na odpowiedź”; surowy token nieznany — demo i tak tylko czyta
        db.add(AvizoFormToken(request_id=req.id, stage=stage,
                              token_hash=hashlib.sha256(secrets.token_bytes(32)).hexdigest(),
                              expires_at=now + dt.timedelta(days=5)))
    return req


def avizo(db, containers: list[Container], company_id: int, forwarder_id: int, author_id: int) -> int:
    """Awizacje w stanach, które widzi logistyka: czeka na spedytora, odpowiedź do decyzji
    (potwierdzenie i prośba o inny termin), odrzucona z komentarzem, etap kierowców, zamknięta."""
    now = utcnow()
    mine = [c for c in containers if c.forwarder_id == forwarder_id and c.notify_date]

    def pick(*statuses):
        return [c for c in mine if c.status in statuses]
    early, mid = pick(S.W_PORCIE, S.ODPRAWA), pick(S.AWIZOWANY)
    late, done = pick(S.W_DOSTAWIE), pick(S.DOSTARCZONY)
    plan = [(AvizoStatus.SENT_STAGE1, early[0:2], {}),
            (AvizoStatus.CONFIRMED_BY_FORWARDER, early[2:4], {"confirmed_at": now}),
            (AvizoStatus.REJECTED, early[4:5],
             {"reject_comment": "Proszę o termin po 10:00 — rampa zajęta rano (dane demo)."}),
            (AvizoStatus.SENT_STAGE2, mid[0:2], {"confirmed_at": now, "approved_by_id": author_id,
                                                 "approved_at": now}),
            (AvizoStatus.DRIVERS_SUBMITTED, late[0:2], {"confirmed_at": now, "approved_at": now}),
            (AvizoStatus.CLOSED, done[0:2], {"confirmed_at": now, "approved_at": now,
                                             "closed_at": now})]
    made = 0
    for status, items, extra in plan:
        if not items:
            continue
        req = _request(db, company_id, forwarder_id, author_id, status, items, now, **extra)
        made += 1
        if status == AvizoStatus.CONFIRMED_BY_FORWARDER:   # jedna zgoda, jedna prośba o zmianę
            first, *rest = items
            db.add(DeliveryConfirmation(request_id=req.id, container_id=first.id, decision="confirmed",
                                        proposed_date=first.notify_date, proposed_time="08:00"))
            for c in rest:
                db.add(DeliveryConfirmation(request_id=req.id, container_id=c.id,
                                            decision="date_change",
                                            proposed_date=c.notify_date + dt.timedelta(days=1),
                                            comment="Kierowca dostępny dzień później (dane demo)."))
    return made
