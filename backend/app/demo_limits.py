"""Ograniczenia widoków kont demo (instancja portfolio, DEMO_READONLY_LOGINS).

Konto demo jest publiczne i współdzielone, a blokada zapisu (`security._enforce_demo_readonly`)
patrzy tylko na metodę HTTP. Tu są odczyty (GET), których demo nie dostaje:
- GET ze skutkiem ubocznym (szkic .eml ustawia obieg WYSLANE, XML SADUE pisze audyt),
- dziennik zmian i audyt (ruch innych gości wspólnego konta),
- paczki ZIP i pełne eksporty (obciążenie serwera, wynoszenie całego zestawu),
- wywołania DLT (linki publiczne dla partnera),
- powiadomienia (wspólna skrzynka wszystkich gości).
Ekrany chowają te miejsca (`frontend/src/demoLimits.ts`); tutaj jest egzekwowanie."""
import re

DEMO_BLOCKED_READS = re.compile("|".join((
    r"^/api/invoice-batches/\d+/(agency-mail\.eml|sadue\.xml)$",
    r"^/api/changes/feed$",
    r"^/api/audit(/|$)",
    r"^/api/containers/\d+/attachments/zip$",
    r"^/api/archive/attachments-zip$",
    r"^/api/containers/export/xlsx$",
    r"^/api/import/sap-imports/\d+/errors\.xlsx$",
    r"^/api/stats/transport-jobs\.csv$",
    r"^/api/pallet-calls(/|$)",
    r"^/api/stock-targets(/|$)",
    r"^/api/notifications(/|$)",
)))

DEMO_BLOCKED_MESSAGE = "Wersja demo — ten widok jest wyłączony."


def blocked_for_demo(path: str) -> bool:
    return DEMO_BLOCKED_READS.match(path) is not None
