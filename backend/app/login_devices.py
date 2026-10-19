"""Mail „logowanie z nowego urządzenia” (czwarta lista PO, pkt 8).

Po udanym logowaniu (także po 2FA) porównujemy przeglądarkę z listą znanych urządzeń konta. Nowa przeglądarka →
mail do właściciela konta: kiedy, skąd (IP), jaka przeglądarka i system, co zrobić, jeśli to nie on.
Pierwsze logowanie konta tylko zapamiętuje urządzenie (bez maila — inaczej każdy nowy użytkownik dostałby
alarm). Konta demo i konta bez adresu e-mail pomijamy.

Zapis bez nowej tabeli (bez migracji): ustawienie `known_devices:{user_id}` z listą skrótów HMAC nagłówka
User-Agent (sam nagłówek nie jest przechowywany). Najwyżej MAX_DEVICES ostatnich urządzeń.
Mail wysyłany w tle i best-effort: błąd wysyłki nigdy nie blokuje logowania."""
from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import logging

from sqlalchemy.orm import Session

from . import app_settings
from .config import settings
from .models import User
from .models.enums import PL_TZ
from .security import is_demo_login

logger = logging.getLogger(__name__)

PREFIX = "known_devices:"
MAX_DEVICES = 10
_BROWSERS = (("Edg/", "Edge"), ("OPR/", "Opera"), ("Firefox/", "Firefox"), ("Chrome/", "Chrome"),
             ("Safari/", "Safari"))
_SYSTEMS = (("Windows", "Windows"), ("Android", "Android"), ("iPhone", "iOS"), ("iPad", "iPadOS"),
            ("Mac OS X", "macOS"), ("Linux", "Linux"))


def fingerprint(user_agent: str) -> str:
    """Skrót przeglądarki — HMAC z kluczem aplikacji, więc z zapisu nie da się odtworzyć nagłówka."""
    raw = (user_agent or "").strip()[:400].encode()
    return hmac.new(settings.secret_key.encode(), raw, hashlib.sha256).hexdigest()[:24]


def describe(user_agent: str) -> str:
    """„Chrome · Windows” — czytelny opis do maila (pierwsze dopasowanie z listy)."""
    ua = user_agent or ""
    browser = next((name for mark, name in _BROWSERS if mark in ua), "nieznana przeglądarka")
    system = next((name for mark, name in _SYSTEMS if mark in ua), "nieznany system")
    return f"{browser} · {system}"


def _load(db: Session, user_id: int) -> list[str]:
    try:
        data = json.loads(app_settings.get_setting(db, f"{PREFIX}{user_id}") or "[]")
    except ValueError:
        return []
    return [str(x) for x in data] if isinstance(data, list) else []


def remember(db: Session, user: User, user_agent: str) -> bool:
    """Zapisuje urządzenie; True = nowe urządzenie konta, które już wcześniej się logowało."""
    known = _load(db, user.id)
    fp = fingerprint(user_agent)
    was_known = fp in known
    rest = [x for x in known if x != fp]
    app_settings.set_setting(db, f"{PREFIX}{user.id}", json.dumps([fp, *rest][:MAX_DEVICES]))
    db.flush()
    return bool(known) and not was_known


def _mail_html(user: User, device: str, ip: str, at: datetime.datetime) -> str:
    from .mail_html import esc
    when = at.astimezone(PL_TZ).strftime("%d.%m.%Y %H:%M")
    return f"""
      <div style="font-family:Segoe UI,Arial,sans-serif;color:#1c2733;max-width:520px">
        <h2 style="color:#10263f">Nowe logowanie / New sign-in</h2>
        <p>Cześć {esc(user.full_name or user.login)},</p>
        <p><b>PL:</b> na Twoje konto <b>{esc(user.login)}</b> w aplikacji Kolejka zalogowano się z urządzenia,
           którego wcześniej nie używałeś.<br>
           <b>EN:</b> your account was used to sign in from a device we haven't seen before.</p>
        <table style="border-collapse:collapse;margin:14px 0">
          <tr><td style="padding:4px 12px 4px 0;color:#64748b">Kiedy / When</td><td>{esc(when)}</td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#64748b">Urządzenie / Device</td><td>{esc(device)}</td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#64748b">Adres IP / IP address</td><td>{esc(ip)}</td></tr>
        </table>
        <p>Jeśli to Ty — nic nie musisz robić. Jeśli nie — zmień hasło („Nie pamiętam hasła” na ekranie
           logowania) i daj znać administratorowi.<br>
           If this was you, no action is needed. If not, reset your password and tell your administrator.</p>
      </div>"""


def check_login(db: Session, user: User, user_agent: str, ip: str) -> None:
    """Wołane po udanym logowaniu (przed commitem). Nigdy nie podnosi wyjątku."""
    if is_demo_login(user.login):
        return
    try:
        new_device = remember(db, user, user_agent)
        if not (new_device and user.email):
            return
        from .notifications import send_html_email
        send_html_email([user.email], "Nowe logowanie na Twoje konto / New sign-in — Kolejka",
                        _mail_html(user, describe(user_agent), ip, datetime.datetime.now(datetime.UTC)))
    except Exception as exc:  # noqa: BLE001 — best-effort: brak SMTP nie może blokować logowania
        logger.warning("Mail o nowym urządzeniu nie wysłany: %s", exc)
