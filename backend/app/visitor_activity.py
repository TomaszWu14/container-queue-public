"""Aktywność gościa demo po wejściu: ile ekranów, jak długo, jakie sekcje (bez IP i user-agenta).

Aplikacja to SPA (React), więc serwer nie widzi przejść między ekranami — front wysyła lekki
sygnał `POST /api/public/demo-visitor/view` z `{path}` przy każdej zmianie trasy na koncie demo.
Liczymy tylko gościa z ważnym, podpisanym ciasteczkiem bramki (id wpisu w JWT); gość z ciasteczkiem
bez id albo z podróbką — nie liczymy. Sekcja = pierwszy segment ścieżki (`/kolejka/12` → `kolejka`,
`/` → `start`), max 40 znaków z [a-z0-9_-]; ścieżki techniczne (api, assets, health…) pomijamy.
Każdy błąd = ostrzeżenie w logu; sygnał nigdy nie psuje odpowiedzi.
"""
import logging
import re

from sqlalchemy import update
from sqlalchemy.orm import Session

from . import demo_visitors, visitor_notify
from .config import settings
from .models import DemoVisitor, utcnow

logger = logging.getLogger(__name__)

MAX_SECTIONS = 20
MAX_SECTION_LEN = 40
_SECTION_RE = re.compile(r"[a-z0-9_-]+")
# nie-ekrany: API, pliki statyczne, monitoring — nawet gdyby ktoś je wysłał w sygnale
SKIPPED = frozenset({"api", "assets", "static", "health", "favicon.ico", "robots.txt", "sw.js",
                     "manifest.webmanifest", "docs", "openapi.json"})


def section_of(path: str) -> str | None:
    """Pierwszy segment ścieżki ekranu albo None (nie liczymy)."""
    if not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
        return None
    first = path.split("?", 1)[0].split("#", 1)[0].strip("/").split("/", 1)[0].lower()
    if not first:
        return "start"
    first = first[:MAX_SECTION_LEN]
    if first in SKIPPED or not _SECTION_RE.fullmatch(first):
        return None
    return first


def duration_min(visitor: DemoVisitor) -> int | None:
    """Czas wizyty ≈ ostatni ekran − wejście, w pełnych minutach (min. 1); None = brak ekranów."""
    if visitor.last_seen_at is None or visitor.created_at is None:
        return None
    return max(1, round((visitor.last_seen_at - visitor.created_at).total_seconds() / 60))


def top_sections(visitor: DemoVisitor, n: int = 3) -> list[str]:
    counts = visitor.sections if isinstance(visitor.sections, dict) else {}
    return [k for k, _ in sorted(counts.items(), key=lambda kv: (-int(kv[1]), kv[0]))[:n]]


def _bump(db: Session, vid: int, section: str) -> tuple[DemoVisitor, int] | None:
    visitor = db.get(DemoVisitor, vid, populate_existing=True)   # świeże sekcje, nie z pamięci sesji
    if visitor is None:
        return None
    sections = dict(visitor.sections) if isinstance(visitor.sections, dict) else {}
    if section in sections or len(sections) < MAX_SECTIONS:   # nowe sekcje ponad limit — pomijamy
        sections[section] = int(sections.get(section, 0)) + 1
    # page_views liczy baza (page_views + 1) — dwa równoległe sygnały nie zgubią ekranu
    views = db.execute(
        update(DemoVisitor).where(DemoVisitor.id == vid)
        .values(page_views=DemoVisitor.page_views + 1, last_seen_at=utcnow(), sections=sections)
        .returning(DemoVisitor.page_views)
        .execution_options(synchronize_session=False)).scalar_one()
    db.commit()
    return visitor, views


def record_view(db: Session, token: str | None, path: str) -> None:
    """Zalicza ekran gościowi z ciasteczka; przy progu NTFY_ENGAGED_VIEWS — jeden push."""
    try:
        vid = demo_visitors.visitor_id(token)
        section = section_of(path)
        if vid is None or section is None:
            return
        bumped = _bump(db, vid, section)
        if bumped is None:
            return
        visitor, views = bumped
        threshold = settings.ntfy_engaged_views
        if threshold and views == threshold:
            visitor_notify.notify_engaged(visitor.first_name, visitor.last_name, visitor.company, views)
    except Exception as exc:  # noqa: BLE001 — statystyka nie może zaszkodzić gościowi
        db.rollback()
        logger.warning("Nie zapisano aktywności gościa demo: %s", type(exc).__name__)
