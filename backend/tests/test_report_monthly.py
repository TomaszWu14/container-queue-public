"""Trzecia lista PO, pkt 8: raport miesięczny dla zarządu — strona HTML do druku / zapisu jako PDF, liczby
w zakresie użytkownika, przycisk drukowania przepuszczany przez CSP (stały skrypt)."""
from app.print_button import PRINT_SCRIPT

from .conftest import login


def test_monthly_report_renders_for_editors(client, admin_headers):
    r = client.get("/api/reports/monthly", headers=admin_headers)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/html")
    html = r.text
    for part in ("Raport miesięczny", "Dostawy i praca zespołu", "Dokumenty i kary za przestój",
                 "Przebieg procesu", "Odczyt faktur", "Automaty (ostatnie 7 dni)", "Z-039"):
        assert part in html
    assert PRINT_SCRIPT in html and "data-print" in html


def test_monthly_report_escapes_and_is_scoped(client, admin_headers):
    """Brak danych innej spółki w liczbach nie da się sprawdzić tekstem — sprawdzamy, że magazyn nie ma dostępu
    (macierz uprawnień) i że w HTML nie ma niezamierzonego wstrzyknięcia (Jinja autoescape)."""
    r = client.get("/api/reports/monthly", headers=admin_headers)
    assert "<script>" not in r.text.replace(PRINT_SCRIPT, "")
    from app.database import SessionLocal
    from app.models import Role, User
    from app.security import hash_password
    with SessionLocal() as db:
        db.add(User(login="mag-report", hashed_password=hash_password("pass12345"), role=Role.warehouse))
        db.commit()
    assert client.get("/api/reports/monthly", headers=login(client, "mag-report", "pass12345")).status_code == 403
