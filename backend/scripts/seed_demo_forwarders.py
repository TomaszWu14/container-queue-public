"""Dane demo: historia awizacji trzech spedycji z 90 dni — żeby „Karta spedytora” (US-079) miała co pokazać.

Zamknięte awizacje z odpowiedziami po różnym czasie (szybka, przeciętna i wolna spedycja), część z prośbą
o inny termin albo z problemem, jedna odesłana do poprawy. Wszystko fikcyjne i deterministyczne."""
import datetime as dt
import secrets

from app.models import AvizoItem, AvizoRequest, AvizoStatus, DeliveryConfirmation, Forwarder

# nazwa spedycji, godziny do odpowiedzi (kolejne awizacje), decyzje po kolei
PROFILES = (
    ("Spedycja Demo", (2, 3, 1.5, 5, 4, 2.5, 6, 3), ("confirmed", "confirmed", "date_change", "confirmed")),
    ("Baltic Freight Demo", (8, 20, 12, 30, 16, 22, 9), ("confirmed", "date_change", "confirmed", "problem")),
    ("Nordic Transport Demo", (36, 50, 28, 70, 44, 26), ("date_change", "problem", "confirmed", "date_change")),
)


def history(db, containers, company_id: int, author_id: int, now: dt.datetime) -> int:
    pool = [c for c in containers if c.company_id == company_id] or list(containers)
    made = 0
    for p, (name, hours, decisions) in enumerate(PROFILES):
        fw = db.query(Forwarder).filter_by(name=name).first()
        if fw is None:
            fw = Forwarder(name=name, email=f"awizacje+{p}@example.com")
            db.add(fw)
            db.flush()
        for i, h in enumerate(hours):
            sent = now - dt.timedelta(days=8 + i * 9 + p, hours=3 * p)
            req = AvizoRequest(token=secrets.token_hex(16), company_id=company_id, forwarder_id=fw.id,
                               created_by_id=author_id, status=AvizoStatus.CLOSED, language="pl",
                               created_at=sent, confirmed_at=sent + dt.timedelta(hours=h),
                               approved_at=sent + dt.timedelta(hours=h + 1), closed_at=sent + dt.timedelta(days=3),
                               expires_at=now + dt.timedelta(days=7),
                               reject_comment="Proszę podać godzinę slotu (dane demo)." if (p == 2 and i == 1) else "")
            db.add(req)
            db.flush()
            for k in range(2):
                c = pool[(p * 17 + i * 2 + k) % len(pool)]
                db.add(AvizoItem(request_id=req.id, container_id=c.id, confirmed=True))
                db.add(DeliveryConfirmation(request_id=req.id, container_id=c.id,
                                            decision=decisions[(i + k) % len(decisions)],
                                            submitted_at=sent + dt.timedelta(hours=h),
                                            comment="" if k == 0 else "dane demo"))
            made += 1
    return made
