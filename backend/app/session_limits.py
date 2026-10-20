"""Limity sesji (ASVS 3.3.2, decyzja PO 2026-10-19): wylogowanie po 30 min bezczynności
i zawsze najpóźniej 12 h po zalogowaniu.

Bezczynność: refresh token jest ważny SESSION_IDLE_MINUTES od ostatniego odświeżenia, a access
token najwyżej połowę tego okna — kto nic nie robi, po tym czasie nie odświeży już sesji. Panel
odświeża sesję tylko przy aktywności użytkownika (ruch, klawisz, dotyk) i sam wylogowuje po
30 min bez aktywności (`frontend/src/idleLogout.ts`).

Limit bezwzględny: refresh token niesie czas zalogowania (`at`), rotacja go przenosi, a żaden
token nie sięga poza `at + SESSION_MAX_HOURS`. Starsze tokeny bez `at` liczą od `iat`."""
import datetime

from fastapi import HTTPException, status

from .config import settings

SESSION_OVER = "Sesja wygasła — zaloguj się ponownie."


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def session_start(payload: dict) -> datetime.datetime:
    """Czas zalogowania zapisany w tokenie (`at`), a w starszych tokenach — `iat`."""
    raw = payload.get("at", payload.get("iat"))
    try:
        return datetime.datetime.fromtimestamp(int(str(raw)), datetime.UTC)
    except (TypeError, ValueError, OverflowError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, SESSION_OVER) from None


def deadline(start: datetime.datetime) -> datetime.datetime:
    return start + datetime.timedelta(hours=settings.session_max_hours)


def _left(start: datetime.datetime, life: datetime.timedelta) -> datetime.timedelta:
    left = min(life, deadline(start) - _now())
    if left.total_seconds() <= 0:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, SESSION_OVER)
    return left


def access_lifetime(start: datetime.datetime | None = None) -> datetime.timedelta:
    """Access token: ACCESS_TOKEN_MINUTES, ale najwyżej pół okna bezczynności i nie poza limit 12 h."""
    minutes = min(settings.access_token_minutes, max(1, settings.session_idle_minutes // 2))
    return _left(start or _now(), datetime.timedelta(minutes=minutes))


def refresh_lifetime(start: datetime.datetime, idle: bool = True) -> datetime.timedelta:
    """Refresh token: okno bezczynności, nie poza limit 12 h od zalogowania.
    idle=False (wspólne konto demo, tylko odczyt): sam limit 12 h — wyjście z karty na pół
    godziny nie wyrzuca odwiedzającego z pokazu."""
    life = datetime.timedelta(minutes=settings.session_idle_minutes) if idle else deadline(start) - _now()
    return _left(start, life)
