# API — opis

[DEV], 2026-10-16, wersja 0.1. Specyfikacja OpenAPI jest generowana przez FastAPI i dostępna **tylko poza
produkcją** pod `/docs`, `/redoc`, `/openapi.json` (na produkcji wyłączone — nie publikujemy pełnej
powierzchni API). Ten plik opisuje konwencje i mapę zasobów; szczegóły pól są w schematach Pydantic
(`backend/app/schemas/`) i w OpenAPI.

## Jak dostać OpenAPI bez uruchamiania serwera

```bash
cd backend
python -c "import json; from app.main import app; print(json.dumps(app.openapi(), ensure_ascii=False))" > openapi.json
```

Propozycja (US-023 lub osobna historyjka): generować `openapi.json` w CI jako artefakt i porównywać
z poprzednim biegiem (wykrywanie niezamierzonych zmian kontraktu).

## Konwencje

| Temat | Zasada |
|---|---|
| Prefiks | wszystko pod `/api`; reszta ścieżek serwuje panel (SPA) |
| Uwierzytelnianie | cookie `timporye_access` (`HttpOnly`) ustawiane przez `POST /api/auth/login`; alternatywnie `Authorization: Bearer <access>` (skrypty, n8n, smoke); token serwisowy `X-Automation-Token` (n8n) |
| Odświeżanie sesji | `POST /api/auth/refresh` — cookie `timporye_refresh`, rotacja przy każdym użyciu |
| CSRF | zapis z cookie wymaga nagłówka `X-Requested-With: XMLHttpRequest` albo `Origin`/`Referer` = adres aplikacji; inaczej 403 |
| Autoryzacja | rola sprawdzana zależnością (`require_roles`), zakres zasobu w `deps.py`; rekord spoza zakresu = **404** (nie 403) |
| Błędy | JSON `{"detail": "komunikat po polsku"}`; 401 brak/zły token, 403 brak roli / CSRF / konto tylko do odczytu, 404 brak lub poza zakresem, 409 konflikt reguły biznesowej lub klucza unikalnego, 410 link wygasł, 413 plik za duży, 422 walidacja, 429 limit (`Retry-After`) |
| Limity | 300 żądań/min na IP dla `/api/*` (bez `/api/health`); logowanie: limity nieudanych prób; publiczne formularze: 30/min |
| Pliki | `multipart/form-data`; limit `MAX_UPLOAD_MB` (25 MB); pobieranie jako `attachment` |
| Daty | ISO 8601 (`YYYY-MM-DD`, `YYYY-MM-DDTHH:MM:SSZ`); strefa prezentacji: Europe/Warsaw w panelu |
| Statusy | wartości enumów po polsku wielkimi literami (`W_PORCIE`, `ODPRAWIONY`) — jak w `models/enums.py` |
| Śledzenie | nagłówek odpowiedzi `X-Request-ID` — podać przy zgłaszaniu błędu |
| Zgodność | zmiana łamiąca kontrakt (usunięcie pola, zmiana typu) wymaga historyjki, wpisu w `CHANGELOG.md` i aktualizacji frontu w tym samym PR (strażnik `test_front_api_paths.py` pilnuje ścieżek) |

## Trasy publiczne (bez logowania)

Lista jawna w `backend/tests/test_routes_require_auth.py` (`PUBLIC`): logowanie i odzyskiwanie konta,
`/api/health`, `/api/health/deep` (sam status), branding ekranu logowania, beacon błędów JS, formularz
awizacji `/api/avizo/{token}…`, formularz kierowcy `/api/avizo/driver/{token}`, wywołania palet
`/api/mag1/{token}…`. Nowa trasa bez `Depends(get_current_user)` nieobecna na tej liście = czerwony test.

## Mapa zasobów (prefiksy routerów)

| Prefiks | Obszar | Router |
|---|---|---|
| `/api/auth` | logowanie, 2FA, reset hasła, profil, sesje | `auth.py` |
| `/api/admin`, `/api/users`, `/api/companies`… | administracja, konta, słowniki, ustawienia, SMS, system | `admin.py`, `dictionaries*.py`, `system.py`, `sms_settings.py` |
| `/api/admin/data-subject` | eksport i anonimizacja danych osoby (RODO) | `data_subject.py` |
| `/api/containers` | kontenery: lista kolejki, karta, statusy, plan, dokumenty, historia, operacje masowe | `containers*.py`, `containers_write.py`, `containers_planning.py` |
| `/api/customs` | odprawa celna, wysyłka dokumentów do agencji | `customs.py` |
| `/api/avizo`, `/api/avizo-requests`, `/api/avizo-proposals`, `/api/avizo-forwarder` | awizacja dwuetapowa (publiczny link i panel) | `avizo*.py` |
| `/api/import`, `/api/sad-import`, `/api/paz` | importy Excel/SAP, PAZ | `imports*.py`, `sad_import.py`, `paz.py` |
| `/api/purchasing`, `/api/purchase-orders` | zakupy, zamówienia | `purchasing.py`, `purchase_orders.py` |
| `/api/suppliers`, `/api/master-data`, `/api/materials`, `/api/supplier-material-maps` | kartoteka dostawców, master data, materiały | `supplier_*.py`, `materials.py`, `master_quality.py` |
| `/api/pallet-calls`, `/api/stock-targets`, `/api/mag1` | wywołania palet, cele zapasu, publiczny link MAG-1 | `pallets.py`, `mag1.py` |
| `/api/notifications`, `/api/presence` | powiadomienia, obecność online | `notifications.py`, `presence.py` |
| `/api/knowledge`, `/api/assistant` | baza wiedzy, asystent (LLM) | `knowledge.py`, `assistant.py` |
| `/api/analytics`, `/api/search`, `/api/audit`, `/api/inbox` | analityka, wyszukiwarka, dziennik zmian, skrzynka | `analytics.py`, `search.py`, `audit_read.py`, `inbox.py` |
| `/api/agency-templates` | szablony pism agencji | `agency_templates.py` |
| `/api/health`, `/api/health/deep` | monitoring | `main.py`, `health.py` |
| pozostałe pod `/api` | zlecenia i wyceny transportu, śledzenie, reklamacje, faktury, poczekalnia, dokumenty, magazyn (brama/rampa), obserwowani, awatary, logi | `forwarding*.py`, `quotes*.py`, `tracking.py`, `complaints*.py`, `invoices.py`, `intake*.py`, `documents.py`, `warehouse_ops.py`, `watchers.py`, `avatars.py`, `logs.py` |

Macierz uprawnień rola × trasa × metoda: `tests/permissions.yaml` (ok. 450 tras).
