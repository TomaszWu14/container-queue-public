"""Ponawianie nieudanych wysyłek (US-022, trzecia lista PO, pkt 1): e-mail, karta w Teams, zdarzenie do n8n.

Wysyłka, która się nie udała (błąd sieci, SMTP, HTTP), wraca do kolejki i jest ponawiana po 1, 5 i 30 min.
Po ostatniej próbie trafia do listy „nie doszło” (ekran Automatyzacje, tylko admin) i do dziennika zadań
(job `delivery_retry`, fn = kanał) — strażnik automatów i licznik błędów widzą ją jak każdy inny błąd.
Zdarzenie do n8n ma przy ponowieniu ten sam `id`, więc odbiorca je zdeduplikuje.

Kolejka żyje w pamięci procesu (kontrakt jednej instancji, jak limiter API) — restart w trakcie ponawiania
gubi oczekujące próby; wynik każdej próby zostaje w dzienniku zadań (Z-036). Opis błędu bez treści
odpowiedzi i adresów (adres wyzwalacza Power Automate zawiera podpis)."""
from __future__ import annotations

import collections
import datetime
import heapq
import itertools
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import httpx

from . import applog
from .models import utcnow

logger = logging.getLogger(__name__)

JOB_NAME = "delivery_retry"
DELAYS_S = (60, 300, 1800)          # po 1, 5 i 30 minutach
TICK_S = 5
MAX_PENDING = 200
MAX_FAILED = 50
AUTO_START = True                   # testy wyłączają wątek i wołają process_due() same


@dataclass(order=True)
class _Item:
    due: float
    seq: int
    channel: str = field(compare=False)
    label: str = field(compare=False)
    fn: Callable = field(compare=False, repr=False)
    args: tuple = field(compare=False, repr=False)
    kwargs: dict = field(compare=False, repr=False)
    attempts: int = field(compare=False, default=1)
    error: str = field(compare=False, default="")


_lock = threading.Lock()
_queue: list[_Item] = []
_failed: collections.deque[dict] = collections.deque(maxlen=MAX_FAILED)
_seq = itertools.count()
_worker: threading.Thread | None = None


def describe(exc: BaseException) -> str:
    """Krótki opis błędu bez treści odpowiedzi i adresów (mogą zawierać sekrety / dane)."""
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    return type(exc).__name__


def attempt(channel: str, label: str, fn: Callable, /, *args, **kwargs) -> bool:
    """Pierwsza próba wysyłki; błąd → kolejka ponowień (bez wyjątku na zewnątrz). True = wysłane."""
    try:
        fn(*args, **kwargs)
        return True
    except Exception as exc:  # noqa: BLE001 — kanał best-effort, wynik idzie do kolejki
        logger.warning("Wysyłka %s nie powiodła się (%s) — ponowię", channel, describe(exc))
        _enqueue(_Item(due=0, seq=0, channel=channel, label=label[:160], fn=fn, args=args, kwargs=kwargs,
                       attempts=1, error=describe(exc)))
        return False


def _enqueue(item: _Item, now: float | None = None) -> None:
    now = time.monotonic() if now is None else now
    item.due = now + DELAYS_S[min(item.attempts, len(DELAYS_S)) - 1]
    item.seq = next(_seq)
    with _lock:
        if len(_queue) >= MAX_PENDING:
            _give_up(item, "kolejka pełna")
            return
        heapq.heappush(_queue, item)
    _ensure_worker()


def _give_up(item: _Item, why: str = "") -> None:
    _failed.appendleft({"channel": item.channel, "label": item.label, "attempts": item.attempts,
                        "error": why or item.error, "at": utcnow().isoformat()})
    applog.record_job(job=JOB_NAME, fn=item.channel, started_at=utcnow(), duration_ms=0, ok=False,
                      detail=f"nie doszło po {item.attempts} próbach: {why or item.error}")


def process_due(now: float | None = None) -> int:
    """Ponawia wysyłki, których czas minął. Zwraca liczbę prób w tym przebiegu."""
    now = time.monotonic() if now is None else now
    due: list[_Item] = []
    with _lock:
        while _queue and _queue[0].due <= now:
            due.append(heapq.heappop(_queue))
    for item in due:
        item.attempts += 1
        started = utcnow()
        try:
            item.fn(*item.args, **item.kwargs)
        except Exception as exc:  # noqa: BLE001
            item.error = describe(exc)
            if item.attempts > len(DELAYS_S):
                _give_up(item)
            else:
                _enqueue(item, now)
            continue
        applog.record_job(job=JOB_NAME, fn=item.channel, started_at=started, duration_ms=0, ok=True,
                          detail=f"doszło za {item.attempts}. razem")
    return len(due)


def _loop() -> None:
    while True:
        time.sleep(TICK_S)
        try:
            process_due()
        except Exception:  # noqa: BLE001 — wątek ponowień nie może umrzeć
            logger.exception("Kolejka ponowień: nieoczekiwany błąd")


def _ensure_worker() -> None:
    global _worker
    if not AUTO_START or (_worker and _worker.is_alive()):
        return
    with _lock:
        if _worker and _worker.is_alive():
            return
        _worker = threading.Thread(target=_loop, name="delivery-retry", daemon=True)
        _worker.start()


def snapshot(now: float | None = None) -> dict:
    """Stan dla ekranu Automatyzacje: oczekujące ponowienia i ostatnie wysyłki, które nie doszły."""
    now = time.monotonic() if now is None else now
    wall = utcnow()
    with _lock:
        pending = sorted(_queue)
    return {
        "pending": [{"channel": i.channel, "label": i.label, "attempts": i.attempts, "error": i.error,
                     "next_at": (wall + datetime.timedelta(seconds=max(0.0, i.due - now))).isoformat()}
                    for i in pending],
        "failed": list(_failed),
        "delays_s": list(DELAYS_S),
    }


def reset() -> None:
    """Testy: czysta kolejka."""
    with _lock:
        _queue.clear()
        _failed.clear()
