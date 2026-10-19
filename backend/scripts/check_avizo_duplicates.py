"""Tylko odczyt: czy baza jest gotowa na migrację uniq001 (US-021)? Liczy zdublowane pozycje awizacji
(ten sam kontener 2× w awizacji) oraz decyzje spedycji spoza listy. Nic nie zmienia.
    DATABASE_URL=... python scripts/check_avizo_duplicates.py   (z backend/)
Kod wyjścia 0 = można migrować, 1 = najpierw decyzja PO, co zachować."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine, text  # noqa: E402

from app.config import settings  # noqa: E402

QUERIES = {
    "avizo_items: ten sam kontener 2× w awizacji":
        "SELECT request_id, container_id, COUNT(*) FROM avizo_items GROUP BY request_id, container_id HAVING COUNT(*) > 1",
    "avizo_delivery_confirmations: decyzja spoza listy":
        "SELECT id, decision, 1 FROM avizo_delivery_confirmations "
        "WHERE decision NOT IN ('confirmed', 'date_change', 'problem')",
}


def main() -> int:
    engine = create_engine(settings.database_url)
    problems = 0
    with engine.connect() as conn:
        for label, sql in QUERIES.items():
            rows = conn.execute(text(sql)).all()
            problems += len(rows)
            print(f"{label}: {len(rows)}")
            for row in rows[:20]:
                print("   ", tuple(row))
    print("OK — można uruchomić migrację uniq001." if not problems else "Najpierw decyzja PO, co zachować.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
