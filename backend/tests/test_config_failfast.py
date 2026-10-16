"""US-001 (R-04, B-005): produkcja odmawia startu bez PostgreSQL w DATABASE_URL.

Bez DATABASE_URL config.py bierze domyślne `sqlite:///./timporye.db` — instancja produkcyjna
wstałaby na pustej bazie plikowej w kontenerze, bez kopii zapasowej, a wpisy znikałyby przy
redeployu. Kryteria akceptacji: docs/analiza/HISTORYJKI.md, US-001."""
import pytest

from app import main
from app.config import settings

PG_URL = "postgresql+psycopg2://timporye:haslo@db:5432/timporye"


@pytest.fixture()
def prod(monkeypatch):
    for name, value in (("environment", "production"), ("secure_cookies", True),
                        ("allow_insecure_http", False), ("secret_key", "x" * 40),
                        ("admin_password", "Silne-Haslo-2026!"),
                        ("public_base_url", "https://kolejka.example.com"),
                        ("automation_api_token", ""), ("bcrypt_rounds", 12),
                        ("database_url", PG_URL)):
        monkeypatch.setattr(settings, name, value)
    return monkeypatch


@pytest.mark.parametrize("url", ["", "sqlite:///./timporye.db", "sqlite://", "mysql://u:p@h/db",
                                 "nie-adres",
                                 "postgresql://u:p@db:abc/x", "postgres://u:p@db/x"])
def test_production_refuses_non_postgres_database(prod, url):
    prod.setattr(settings, "database_url", url)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        main.validate_settings()


@pytest.mark.parametrize("url", [PG_URL, "postgresql://u:p@db:5432/timporye",
                                 "postgresql+psycopg://u:p@db/timporye"])
def test_production_starts_with_postgres(prod, url):
    prod.setattr(settings, "database_url", url)
    main.validate_settings()   # bez wyjątku


def test_dev_still_starts_on_sqlite(prod):
    prod.setattr(settings, "environment", "dev")
    prod.setattr(settings, "database_url", "sqlite:///./timporye.db")
    main.validate_settings()   # tylko ostrzeżenie w logu, jak dla innych ustawień
