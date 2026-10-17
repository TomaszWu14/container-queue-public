# ADR-0004 · Publiczne API tylko do odczytu z kluczami per firma

- **Status:** proponowana — czeka na akceptację PO (pomysł 7, „wdrażaj wszystko” 2026-10-16)
- **Data:** 2026-10-16
- **Role:** [DEV] propozycja, [SEC] przegląd STRIDE niżej, [BA] pytania do PO na końcu

## Kontekst

Partnerzy (spółki grupy, ich ERP, spedytor) chcą pobierać stan swoich kontenerów automatycznie zamiast
eksportu Excela. Dziś są dwie drogi do API: sesja użytkownika (cookie / Bearer JWT, krótkie tokeny) i jeden
token serwisowy n8n (`X-Automation-Token`, `automation_policy.py`) — wspólny, z rolą konta serwisowego,
bez podziału na firmy. Dokumentacja OpenAPI jest na produkcji wyłączona (`main.py`, `_docs_kw`).

## Rozważane opcje

1. **Udostępnić token n8n partnerom.** Zero kodu. Odrzucone: jeden sekret dla wszystkich, zakres całej grupy,
   brak rozliczalności i odwołania pojedynczej firmy.
2. **Konto użytkownika „integracja” na firmę + logowanie hasłem z ERP.** Działa dziś. Wady: hasło w ERP,
   tokeny wygasają po minutach (odświeżanie w ERP), ślad w audycie miesza ludzi z systemami.
3. **Klucze API per firma, tylko do odczytu, osobna przestrzeń `/api/v1/public/…`.** Klucz należy do spółki
   (`company_id`), ma nazwę, datę wygaśnięcia i listę zakresów; w bazie tylko SHA-256 (jak linki awizacji,
   FR-019). Zakres danych = ta sama izolacja co dla użytkownika tej spółki (`scope_containers` w `deps.py`, D9).
4. **OAuth2 client credentials.** Standard dla dużych integracji; za ciężkie na obecną skalę (kilka spółek).

## Decyzja (proponowana)

Opcja 3, w dwóch krokach:

- **Krok 1 (MVP):** `GET /api/v1/public/containers` i `GET /api/v1/public/containers/{container_no}`
  — pola kolejki bez danych osobowych kierowcy, stronicowanie, filtr `updated_since`. Nagłówek
  `Authorization: ApiKey <klucz>`. Klucz tworzy admin w panelu (pokazany **raz**), odwołanie jednym klikiem.
  Strona `/api-docs` z opisem i przykładami (curl, Python, Excel Power Query) — generowana ze schematu
  tylko dla tras publicznych, nie całego API.
- **Krok 2 (po zgłoszeniu potrzeby):** webhooki „zmiana statusu” z podpisem HMAC (wzór: webhook n8n).

Zapis przez API **nie** wchodzi w zakres — każdy zapis wymagałby osobnego ADR.

## Przegląd bezpieczeństwa [SEC] — STRIDE dla nowego przepływu F-API

| Zagrożenie | Ryzyko | Kontrola w projekcie |
|---|---|---|
| **S** kradzież / odgadnięcie klucza | wyciek danych spółki | 32 bajty losowe (`secrets.token_urlsafe`), w bazie SHA-256, porównanie stałoczasowe; prefiks klucza do rozpoznania w logach i skanerach sekretów; data wygaśnięcia obowiązkowa (domyślnie 12 mies.) |
| **T** zmiana danych | — | tylko GET; trasy publiczne nie mają metod zapisu (test macierzy uprawnień `permissions.yaml`) |
| **R** kto pobrał dane | spór z partnerem | wpis w dzienniku: klucz (id, nie wartość), trasa, liczba rekordów, IP; licznik „ostatnie użycie” w panelu |
| **I** dostęp do innej spółki | **wysokie** | klucz → `company_id` → ta sama izolacja co użytkownik (`deps.py`, D9); bez parametru `company_id` w zapytaniu; test „klucz spółki A nie widzi B” jako kryterium akceptacji; bez danych kierowcy (RODO) |
| **D** zalewanie zapytaniami | spowolnienie panelu | limit na klucz (np. 60/min) i maks. 500 rekordów na stronę; 429 z `Retry-After` |
| **E** klucz jako furtka do reszty API | **wysokie** | klucz akceptowany **tylko** w routerze `/api/v1/public`; `get_current_user` go nie zna; CSRF nie dotyczy (bez cookie) |

Nowe ryzyka do `RYZYKA.md`: wyciek klucza u partnera (prawdopodobieństwo średnie, wpływ: dane jednej spółki).
Procedura odwołania i rotacji w `RUNBOOK.md`. Poziom ASVS L2: V2.10 (sekrety usług), V4.1, V13 (API).

## Konsekwencje

- Migracja: tabela `api_keys` (id, company_id, name, key_hash, prefix, scopes, created_by, expires_at,
  revoked_at, last_used_at). Jedna nowa strona admina, jedna strona dokumentacji.
- Kontrakt `/api/v1` jest wersjonowany: zmiana niezgodna = `/api/v2`, stara wersja żyje min. 3 miesiące.
- Demo: klucz pokazowy tylko do danych demo (sygnał „gotowe do integracji”).

## Pytania do PO (bez odpowiedzi — nie zaczynamy kodu)

1. Kto dostaje klucze w pierwszej kolejności — spółki grupy (ERP), spedytor, ktoś inny?
2. Jakie pola są potrzebne partnerom (np. status, ETA, data dostawy, magazyn, odprawa)? Czy stan odprawy
   może wyjść poza grupę?
3. Czy w kroku 1 wystarczy pobieranie co jakiś czas (bez webhooków)?
