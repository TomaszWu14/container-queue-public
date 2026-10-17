"""Zdarzenia wysyłane do n8n / Power Automate / Make (US-035, pomysł 9 PO).

Wysyłka i podpis były w `notifications` (kanał best-effort, w tle). Tu jest jedno miejsce,
które: buduje kopertę zdarzenia (id do deduplikacji po stronie odbiorcy, wersja formatu),
podpisuje DOKŁADNIE wysyłane bajty (HMAC-SHA256, nagłówek X-Timporye-Signature), sprawdza
odpowiedź (błąd HTTP = wyjątek) i zapisuje wynik każdej wysyłki w dzienniku zadań
(job „n8n_events”, fn = rodzaj zdarzenia). Z dziennika liczy ekran „Automatyzacje”
(przebiegi, błędy), a nieudana wysyłka zapala dzwonek admina (applog._alert).

Format: docs/ZDARZENIA-N8N.md.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid

import httpx

from . import applog
from .config import settings
from .models import utcnow

JOB_NAME = "n8n_events"
FORMAT_VERSION = 1
SIGNATURE_HEADER = "X-Timporye-Signature"


def sign_payload(body: bytes, secret: str) -> str:
    """Podpis treści webhooka (HMAC-SHA256, format jak w GitHubie) — odbiorca weryfikuje go
    przed wykonaniem workflow, żeby triggera nie odpalił ktokolwiek znający adres."""
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def envelope(kind: str, title: str, body: str = "", **fields) -> dict:
    return {"id": uuid.uuid4().hex, "version": FORMAT_VERSION, "source": "timporye",
            "event": kind, "title": title, "body": body,
            "sent_at": utcnow().isoformat(), **fields}


def post(url: str, payload: dict) -> int:
    """Wysyła zdarzenie i zapisuje wynik w dzienniku zadań; błąd sieci/HTTP = wyjątek.

    Serializujemy raz i wysyłamy dokładnie te bajty, które podpisaliśmy — inaczej podpis
    nie zgadzałby się po stronie odbiorcy (separatory, kolejność kluczy)."""
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    headers = {"Content-Type": "application/json"}
    if settings.automation_webhook_secret:
        headers[SIGNATURE_HEADER] = sign_payload(data, settings.automation_webhook_secret)
    started_at, start = utcnow(), time.perf_counter()
    kind = str(payload.get("event", ""))[:120]
    try:
        response = httpx.post(url, content=data, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as exc:
        applog.record_job(job=JOB_NAME, fn=kind, started_at=started_at,
                          duration_ms=int((time.perf_counter() - start) * 1000), ok=False,
                          detail=f"{type(exc).__name__}: {exc}"[:300])
        raise
    applog.record_job(job=JOB_NAME, fn=kind, started_at=started_at,
                      duration_ms=int((time.perf_counter() - start) * 1000), ok=True, detail="1")
    return response.status_code
