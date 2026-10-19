# API — trasy i uprawnienia

Wygenerowane z kodu: `python scripts/export_api_docs.py` (z `backend/`). Pełny opis z typami pól:
[`openapi.json`](openapi.json) — można go wczytać w Swagger Editor, Postmanie albo n8n.
Konwencje (logowanie, CSRF, błędy, stronicowanie): [API.md](API.md).

**481 operacji w 45 grupach.** Kolumna „Kto ma dostęp” pochodzi z macierzy uprawnień
([`tests/permissions.yaml`](../../tests/permissions.yaml)); zgodność macierzy z kodem sprawdza test.
Dostęp do konkretnych rekordów zawęża dodatkowo zakres spółki / partnera (izolacja danych).
Na produkcji `/docs` i `/openapi.json` są wyłączone — ten plik jest jedynym publicznym opisem.

## admin

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/companies` | List Companies | admin, logistics |
| POST | `/api/companies` | Create Company | admin |
| PATCH | `/api/companies/{company_id}` | Update Company | admin |
| GET | `/api/customs-agencies` | Admin List Customs Agencies | admin |
| POST | `/api/customs-agencies` | Create Customs Agency | admin |
| DELETE | `/api/customs-agencies/{agency_id}` | Delete Customs Agency | admin |
| PATCH | `/api/customs-agencies/{agency_id}` | Update Customs Agency | admin |
| GET | `/api/users` | List Users | admin |
| POST | `/api/users` | Create User | admin |
| GET | `/api/users/access-review` | Przegląd dostępów: konta nieużywane, admini bez 2FA, dostęp do wszystkich spółek (US-076). | admin |
| DELETE | `/api/users/{user_id}` | Usunięcie konta = dezaktywacja + anonimizacja danych osobowych (OBS-002). | admin |
| PATCH | `/api/users/{user_id}` | Update User | admin |
| POST | `/api/users/{user_id}/reset-invite` | Ponowne zaproszenie: nowe losowe hasło tymczasowe + wymuszenie zmiany przy | admin |

## administracja

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/admin/data-subject` | Wszystkie miejsca z danymi osoby (JSON do przekazania osobie). E-mail / imię i nazwisko | admin |
| POST | `/api/admin/data-subject/anonymize-driver` | Usunięcie danych kierowcy na żądanie: kontenery (wpis w audycie z adminem jako autorem), | admin |
| GET | `/api/admin/sms-settings` | Get Sms Settings | admin |
| PUT | `/api/admin/sms-settings` | Put Sms Settings | admin |
| PUT | `/api/admin/theme-colors` | Put Theme Colors | admin |
| GET | `/api/theme-colors` | Każdy zalogowany — kolory obowiązują wszystkich, niezależnie od roli. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |

## agencja celna

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/customs/agencies` | Aktywne agencje celne — do wyboru przy zlecaniu odprawy. | admin, logistics |
| GET | `/api/customs/board` | Tablica odpraw. | admin, logistics, customs |
| GET | `/api/customs/case-statuses` | List Case Statuses | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/customs/case-statuses` | Create Case Status | admin |
| DELETE | `/api/customs/case-statuses/{status_id}` | Delete Case Status | admin |
| PATCH | `/api/customs/case-statuses/{status_id}` | Update Case Status Entry | admin |
| POST | `/api/customs/containers/{container_id}/agent` | Agencja celna wyznacza/zmienia agenta prowadzącego odprawę. Nasi pracownicy powiadomieni. | admin, logistics, customs |
| POST | `/api/customs/containers/{container_id}/assign` | Logistyka zleca odprawę agencji celnej (lub zmienia agencję). | admin, logistics |
| POST | `/api/customs/containers/{container_id}/case-status` | Ustawienie statusu sprawy ze słownika (obie strony). Druga strona powiadomiona. | admin, logistics, customs |
| POST | `/api/customs/containers/{container_id}/send-docs` | Wysyłka dokumentów do agencji: załączniki kontenera trafiają do wiadomości agencji. | admin, logistics, purchasing |
| POST | `/api/customs/containers/{container_id}/status` | Zmiana statusu odprawy (obie strony). Powiadamiana jest druga strona. | admin, logistics, customs |
| POST | `/api/customs/containers/{container_id}/unassign` | Logistyka wycofuje zlecenie odprawy (odpina agencję). | admin, logistics |
| GET | `/api/customs/document-types` | List Document Types | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/customs/document-types` | Create Document Type | admin |
| DELETE | `/api/customs/document-types/{type_id}` | Delete Document Type | admin |
| PATCH | `/api/customs/document-types/{type_id}` | Update Document Type | admin |

## analityka

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/analytics/operational` | KPI operacyjne kontenerów (W6/W15): rozkład statusów, przepustowość miesięczna, | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/analytics/upload` | Upload | admin, logistics |

## asystent

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/assistant/ask` | Ask | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/assistant/examples` | US-039: przykładowe pytania z danych widocznych dla użytkownika (klik = gotowa odpowiedź). | admin, logistics, warehouse, forwarder, customs, purchasing |

## audyt

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/audit` | List Audit | admin |

## auth

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/auth/2fa/enable` | Aktywacja 2FA: kod z aplikacji potwierdza, że sekret został zeskanowany. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/auth/2fa/setup` | W14 #49: wygenerowanie sekretu TOTP (aktywacja w /2fa/enable). Każda rola (SEC-006); | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/auth/2fa/verify` | Drugi krok logowania: kod TOTP lub kod zapasowy po poprawnym haśle. | publiczna (link z tokenem / logowanie) |
| POST | `/api/auth/change-password` | Zmiana własnego hasła przez zalogowanego użytkownika. Używane m.in. przy | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/auth/forgot-password` | Wysyła link resetu na e-mail konta. Zawsze zwraca 202 (bez zdradzania, | publiczna (link z tokenem / logowanie) |
| POST | `/api/auth/login` | Login | publiczna (link z tokenem / logowanie) |
| POST | `/api/auth/logout` | Wylogowanie ze wszystkich urządzeń: podbija wersję sesji (unieważnia access | publiczna (link z tokenem / logowanie) |
| GET | `/api/auth/me` | Me | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/auth/me/prefs` | Profil widoku UI (kolumny/gęstość/zapisane widoki) — podąża za kontem. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| PUT | `/api/auth/me/prefs` | Save My Prefs | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| PATCH | `/api/auth/me/settings` | Wąski self-update: dziś tylko przełącznik „powiadomienia tylko o obserwowanych". | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/auth/refresh` | Refresh | publiczna (link z tokenem / logowanie) |
| POST | `/api/auth/reset-password` | Ustawia nowe hasło na podstawie jednorazowego tokenu; unieważnia wszystkie sesje. | publiczna (link z tokenem / logowanie) |
| GET | `/api/auth/sessions` | My Sessions | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/auth/sessions/revoke-others` | Wyloguj wszystkie inne sesje (bieżący refresh token zostaje). | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| DELETE | `/api/auth/sessions/{session_id}` | Revoke My Session | admin, logistics, warehouse, forwarder, customs, purchasing, sales |

## automations

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/automations` | List Automations | admin, logistics |
| GET | `/api/automations/ai-quality` | US-037: odczyt faktur — reguły / ML / człowiek tydzień po tygodniu i trafność podpowiedzi | admin, logistics |
| GET | `/api/automations/ai-quality/mistakes` | Druga lista PO, pkt 8: pozycje faktur, w których człowiek poprawił podpowiedź modelu (zakres spółek). | admin, logistics |
| GET | `/api/automations/deliveries` | US-022: wysyłki czekające na ponowienie i te, które nie doszły (tylko admin — tytuły alertów | admin |
| GET | `/api/automations/eta-reliability` | Punktualność armatorów (mediana spóźnienia wg historii) i realne ETA kontenerów w drodze. | admin, logistics |
| PUT | `/api/automations/minutes` | Set Minutes | admin |
| GET | `/api/automations/process` | US-038: czas w etapach procesu z historii statusów, cofnięcia i kontenery utknięte dłużej | admin, logistics |
| GET | `/api/automations/rules` | List Rules | admin, logistics |
| PUT | `/api/automations/rules` | Save Rules | admin |
| GET | `/api/automations/rules/backtest` | Ile alertów wysłałaby reguła w ostatnich 30 dniach — w zakresie użytkownika, bez zapisu. | admin, logistics |
| GET | `/api/automations/rules/history` | Ostatnie zmiany reguł: kto, kiedy, co (dodanie / zmiana pól / usunięcie). | admin, logistics |
| POST | `/api/automations/rules/history/{audit_id}/restore` | Przywraca jedną regułę do stanu sprzed wybranej zmiany (też z wpisem w historii). | admin |
| GET | `/api/automations/rules/preview` | Ile otwartych kontenerów spełnia warunek dziś — tylko w zakresie użytkownika. | admin, logistics |
| GET | `/api/automations/simulate-day` | US-040: „Symuluj dzień” — prawdziwe funkcje automatów na danych użytkownika, BEZ zapisu | admin, logistics |
| POST | `/api/automations/test-event` | US-035: zdarzenie testowe do n8n wysłane od razu (nie w tle), żeby admin zobaczył wynik. | admin |
| GET | `/api/automations/what-if` | Druga lista PO, pkt 10: „co jeśli statek spóźni się N dni” — bez zapisu. Bez statku: lista statków. | admin, logistics |
| PUT | `/api/automations/{key}/enabled` | Druga lista PO, pkt 6: admin włącza / wyłącza automat z harmonogramu; zmiana w dzienniku zmian. | admin |
| GET | `/api/reports/monthly` | Monthly Report | admin, logistics |

## awatar

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| DELETE | `/api/me/avatar` | Delete Avatar | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/me/avatar` | Upload Avatar | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/users/{user_id}/avatar` | Get Avatar | admin, logistics, warehouse, forwarder, customs, purchasing, sales |

## awizacja

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/avizo-forwarder` | Otwarte awizacje: spedytor — swoje, logistyka — swoich spółek. | admin, logistics, forwarder |
| GET | `/api/avizo-forwarder/{request_id}` | Formularz etapu 1 / 2 w aplikacji (ten sam kształt co z linku); 409 = nic do wysłania. | admin, logistics, forwarder |
| POST | `/api/avizo-forwarder/{request_id}/confirm` | Confirm | admin, logistics, forwarder |
| POST | `/api/avizo-forwarder/{request_id}/drivers` | Drivers | admin, logistics, forwarder |
| POST | `/api/avizo-forwarder/{request_id}/propose` | Propose | admin, logistics, forwarder |
| GET | `/api/avizo-forwarder/{request_id}/slots` | Slots | admin, logistics, forwarder |
| GET | `/api/avizo-proposals` | List Proposals | admin, logistics |
| POST | `/api/avizo-proposals/{proposal_id}/accept` | Akceptacja jednym klikiem: termin (confirm_plan) + proponowana godzina jako slot, | admin, logistics |
| POST | `/api/avizo-proposals/{proposal_id}/reject` | Odrzucenie z powodem — powód wraca na publiczny link awizacji. | admin, logistics |
| GET | `/api/avizo-requests` | List Requests | admin, logistics |
| GET | `/api/avizo-requests/{request_id}` | Get Request | admin, logistics |
| POST | `/api/avizo-requests/{request_id}/approve` | Approve | admin, logistics |
| POST | `/api/avizo-requests/{request_id}/cancel` | Cancel | admin, logistics |
| POST | `/api/avizo-requests/{request_id}/reject` | Reject | admin, logistics |
| POST | `/api/avizo-requests/{request_id}/resend` | Resend | admin, logistics |
| POST | `/api/avizo-requests/{request_id}/revoke` | Revoke | admin, logistics |
| GET | `/api/avizo/driver/{token}` | Formularz etapu 2 — kontenery zatwierdzone w etapie 1 (bez istniejących danych osobowych). | publiczna (link z tokenem / logowanie) |
| POST | `/api/avizo/driver/{token}` | Etap 2: dane kierowców → Container.driver_* (audyt maskuje telefon/dowód). Jednorazowo. | publiczna (link z tokenem / logowanie) |
| POST | `/api/avizo/send` | Etap 1: zlecenie awizacji per (spedytor, spółka) + mail z jednorazowym linkiem. | admin, logistics |
| GET | `/api/avizo/{token}` | Formularz etapu 1 (dostęp po tokenie z e-maila, bez logowania) — tylko do odczytu | publiczna (link z tokenem / logowanie) |
| POST | `/api/avizo/{token}` | Etap 1: decyzja per kontener (potwierdzam / zmiana terminu / problem). Jednorazowo — | publiczna (link z tokenem / logowanie) |
| POST | `/api/avizo/{token}/propose` | Dostawca/spedycja proponuje inny dzień/godzinę na publicznym linku awizacji. | publiczna (link z tokenem / logowanie) |
| GET | `/api/avizo/{token}/slots` | Wolne sloty dla kontenera z tego zaproszenia na wskazany dzień (zmiana daty w formularzu). | publiczna (link z tokenem / logowanie) |

## checklista

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/checklist-points` | List Points | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/checklist-points` | Create Point | admin |
| PATCH | `/api/checklist-points/{point_id}` | Update Point | admin |
| GET | `/api/containers/{container_id}/checklist` | Get Checklist | admin, logistics, warehouse, forwarder, customs, purchasing |
| PUT | `/api/containers/{container_id}/checklist` | Upsert wyników podanych punktów (pozostałe zostają bez zmian). | admin, logistics, warehouse |

## consolidation

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/consolidation/containers` | List Consolidation Containers | admin, logistics, purchasing |
| GET | `/api/consolidation/proposals` | Tylko odczyt: propozycje pogrupowania koszyka (gotowe do konsolidacji zamowienia | admin, logistics, purchasing |
| POST | `/api/containers/{cid}/close-consolidation` | Close Consolidation | admin, logistics |
| DELETE | `/api/containers/{cid}/orders/{po_id}` | Remove Order | admin, logistics |
| PUT | `/api/containers/{cid}/orders/{po_id}` | Assign Order | admin, logistics |
| GET | `/api/containers/{container_id}/orders` | Container Orders | admin, logistics, purchasing |
| POST | `/api/purchase-orders/{po_id}/block` | Block Order | admin, logistics |
| PATCH | `/api/purchase-orders/{po_id}/crd` | Update Crd | admin, logistics, purchasing |
| POST | `/api/purchase-orders/{po_id}/release` | Release Order | admin, logistics, purchasing |
| POST | `/api/purchase-orders/{po_id}/unblock` | Unblock Order | admin, logistics |

## dane materiałowe

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/import/sp-materials` | Import Sp Materials | admin |
| GET | `/api/sp-materials/import-status` | Import Status | admin, logistics |
| GET | `/api/sp-materials/sheets` | List Sheets | admin, logistics |
| GET | `/api/sp-materials/sheets/{name}` | Sheet Rows | admin, logistics |

## dokumenty

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/containers/{container_id}/archive` | Upload Archive | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/containers/{container_id}/document-tiles` | Document Tiles | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/containers/{container_id}/intake` | Pasek „N dokumentów czeka na potwierdzenie” (decyzja 12). | admin, logistics, forwarder, customs, purchasing |
| POST | `/api/containers/{container_id}/intake` | Upload Intake | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/document-tiles` | Mini-kafelki kolejki (spec 2026-10-06 decyzja 28): PI·CI·PL·BL·SAD + braki + liczba części | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/intake/inbox` | Automat (n8n, token X-Automation-Token; docs/POCZTA-DO-POCZEKALNI.md): cały mail albo | admin, logistics |
| PATCH | `/api/intake/items/{item_id}` | Update Intake Item | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/intake/items/{item_id}/file` | Download Intake Item | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/intake/unmatched` | Poczta bez dopasowania — oczekujące wgrania bez kontenera ze spółek w zakresie. | admin, logistics |
| GET | `/api/intake/{batch_id}` | Get Intake | admin, logistics, forwarder, customs, purchasing |
| POST | `/api/intake/{batch_id}/confirm` | Confirm Intake | admin, logistics, forwarder, customs, purchasing |
| POST | `/api/intake/{batch_id}/discard` | Discard Intake | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/invoice-jobs/{job_id}/pdf` | Część PDF dokumentu z paczki faktur (po cięciu pypdf) — podgląd w przeglądarce. | admin, logistics, purchasing |

## dokumenty (W5)

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/archive/attachments-zip` | Archiwum kolejki: ZIP dokumentów miesiąca per spółka (YYYY-MM). | admin, logistics |
| POST | `/api/attachment-suggestions/{suggestion_id}/accept` | Akceptacja: kopiuje plik części PDF (wycinek stron ze splittera) jako zwykły | admin, logistics, purchasing |
| POST | `/api/attachment-suggestions/{suggestion_id}/reject` | Reject Suggestion | admin, logistics, purchasing |
| GET | `/api/containers/{container_id}/attachment-suggestions` | List Suggestions | admin, logistics, purchasing |
| GET | `/api/containers/{container_id}/attachments/zip` | „Pobierz wszystkie (ZIP)” — załączniki kontenera jednym plikiem. | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/containers/{container_id}/cmr` | #19 — drukowalny list przewozowy (CMR) wypełniony danymi kontenera. HTML z print-CSS | admin, logistics, warehouse, forwarder |
| GET | `/api/customs/containers/{container_id}/send-docs/preview` | Podgląd wiadomości do agencji przed wysyłką (wyrenderowany szablon). | admin, logistics, purchasing |
| GET | `/api/customs/doc-templates` | List Doc Templates | admin, logistics, purchasing |
| POST | `/api/customs/doc-templates` | Create Doc Template | admin |
| DELETE | `/api/customs/doc-templates/{template_id}` | Delete Doc Template | admin |
| PATCH | `/api/customs/doc-templates/{template_id}` | Update Doc Template | admin |
| GET | `/api/customs/docs-gaps` | Kontenery w obiegu celnym z ETA ≤ dziś+DOCS_ETA_DAYS i brakami wymaganych | admin, logistics |
| GET | `/api/documents/search` | #41 — archiwum dokumentów z wyszukiwaniem pełnotekstowym po WSZYSTKICH źródłach | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/invoice-jobs/{job_id}/order-compare` | #34: kwoty i ilości faktury vs zamówienie (EKKO + pozycje). Sam raport. | admin, logistics, purchasing |
| GET | `/api/invoice-jobs/{job_id}/packing-compare` | #33: packing lista (OCR) vs pozycje zamówień kontenera. Sam raport — | admin, logistics, purchasing |

## faktury

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/containers/{container_id}/invoice-batches` | List Invoice Batches | admin, logistics, purchasing |
| POST | `/api/containers/{container_id}/invoice-batches` | Upload Invoices | admin, logistics, purchasing |
| DELETE | `/api/invoice-batches/{batch_id}` | Usuwa paczkę z dokumentami i plikami części; gotowy Excel (załącznik) zostaje. | admin, logistics, purchasing |
| POST | `/api/invoice-batches/{batch_id}/agency-ack` | Agency Ack | admin, logistics, purchasing |
| GET | `/api/invoice-batches/{batch_id}/agency-mail.eml` | Agency Mail Eml | admin, logistics, purchasing |
| GET | `/api/invoice-batches/{batch_id}/agency-mail/preview` | Podgląd szkicu: dokładnie to, co trafi do .eml, plus ostrzeżenia — bez wpisu w audycie. | admin, logistics, purchasing |
| POST | `/api/invoice-batches/{batch_id}/export` | Excel z zatwierdzonych dokumentów paczki. 409 dopóki nie wszystkie zatwierdzone | admin, logistics, purchasing |
| GET | `/api/invoice-batches/{batch_id}/sad-drafts` | Sad State | admin, logistics, purchasing |
| POST | `/api/invoice-batches/{batch_id}/sad-drafts` | Upload Sad Draft | admin, logistics, purchasing |
| POST | `/api/invoice-batches/{batch_id}/sad-drafts/{draft_id}/compare` | Compare Sad Draft | admin, logistics, purchasing |
| POST | `/api/invoice-batches/{batch_id}/sad-drafts/{draft_id}/decision` | Sad Decision | admin, logistics, purchasing |
| GET | `/api/invoice-batches/{batch_id}/sad-drafts/{draft_id}/pages/{page}` | Sad Draft Page | admin, logistics, purchasing |
| POST | `/api/invoice-batches/{batch_id}/sad-drafts/{draft_id}/xml` | XML z WinSAD dosłany po PDF → dane tej wersji z XML i od razu nowe porównanie z fakturami. | admin, logistics, purchasing |
| GET | `/api/invoice-batches/{batch_id}/sadue.xml` | XML SADUE (WinSAD) z zatwierdzonych faktur — ten sam co w mailu; 409 = co poprawić. | admin, logistics, purchasing |
| GET | `/api/invoice-batches/{batch_id}/symbols.xlsx` | Kartoteka symboli do obejrzenia przed wysyłką (ta sama co w mailu). | admin, logistics, purchasing |
| GET | `/api/invoice-conformity/report` | Jednorazowy przegląd wstecz (spec 2026-10-01, PR 4): ostatnie dokumenty paczek faktur, | admin, logistics |
| GET | `/api/invoice-jobs/{job_id}` | Get Invoice Job | admin, logistics, purchasing |
| GET | `/api/invoice-jobs/{job_id}/checks` | Get Job Checks | admin, logistics, purchasing |
| GET | `/api/invoice-jobs/{job_id}/conformity` | Zgodność dokumentu z kontenerem paczki: status ok / uncertain / conflict + sygnały. | admin, logistics, purchasing |
| POST | `/api/invoice-jobs/{job_id}/copy` | „Dodaj też do X”: faktura na kilka kontenerów — tylko do kontenera z jej treści. | admin, logistics, purchasing |
| POST | `/api/invoice-jobs/{job_id}/ignore` | Dokument rozpoznany jako faktura, którym nie jest (certyfikat, list przewozowy bez | admin, logistics, purchasing |
| POST | `/api/invoice-jobs/{job_id}/link-orders` | Świadome przypięcie zamówień z faktury do kontenera paczki (decyzja człowieka). | admin, logistics, purchasing |
| POST | `/api/invoice-jobs/{job_id}/move` | „Wrzuć do X”: dokument w złym kontenerze → właściwy (ta sama spółka). | admin, logistics, purchasing |
| POST | `/api/invoice-jobs/{job_id}/reprocess` | Ponowna ekstrakcja (np. po dopisaniu mapy kolumn u dostawcy) — dla dokumentów | admin, logistics, purchasing |
| PUT | `/api/invoice-jobs/{job_id}/review` | Zapis poprawek operatora (+ opcjonalne zatwierdzenie). Zatwierdzony dokument | admin, logistics, purchasing |
| POST | `/api/sad-drafts/inbox` | Automat (n8n, token X-Automation-Token): PDF/XML draftu z maila agencji → paczka faktur | admin, logistics, purchasing |

## import

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/import/container-ports` | Import słownika portów kontenerowych (xlsx albo tsv/csv). Master data globalne. | admin |
| POST | `/api/import/containers` | Import Containers | admin, logistics |
| POST | `/api/import/mag1-stock` | Import stanów MAG-1 z xlsx — snapshot (każdy import kasuje poprzedni). | admin |
| POST | `/api/import/master-data` | Wspólny dropzone „Wgraj plik master data": typ rozpoznany po nagłówkach, | admin, logistics |
| POST | `/api/import/material-units` | Import przeliczników jednostek materiałów (MARM) z SAP — master data globalne. | admin |
| POST | `/api/import/order-items` | Import zawartości kontenerów (pozycje REF) z eksportu SAP. | admin, logistics |
| POST | `/api/import/purchase-orders` | Import zamówień zakupowych z arkusza ETD. Upsert po (spółka, order_no) — | admin, logistics |
| POST | `/api/import/queue-sync` | Ręczny upload arkusza kolejki (dawniej n8n z SharePointa) → uzgodnienie | admin, logistics |
| GET | `/api/import/queue-sync-date-from` | Ostatnio użyta data „importuj od" dla spółki — do prefillu pola w modalu. | admin, logistics |
| GET | `/api/import/sap-imports/{import_id}/errors.xlsx` | Raport błędów importu SAP (wiersze pominięte) jako xlsx. | admin, logistics |
| POST | `/api/import/sap-orders` | Import nagłówków zamówień zakupu (EKKO) z SAP — „co płynie, skąd i kiedy”. | admin, logistics |
| POST | `/api/import/sharepoint-sync` | Ręczna synchronizacja kolejki z arkusza SharePoint (okres dwutorowej pracy Excel ↔ aplikacja). | admin, logistics |
| POST | `/api/import/suppliers-lfa1` | Import kartoteki dostawców z eksportu SAP LFA1 z podglądem (importers/lfa1.py). | admin, logistics |
| GET | `/api/import/templates/{kind}` | Import Template | admin, logistics |

## import SAD

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/sad-import/check` | Check Sad | admin, logistics, purchasing |
| POST | `/api/sad-import/report` | Sad Report | admin, logistics, purchasing |

## inbox

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/inbox` | Inbox | admin, logistics, forwarder, customs, purchasing |

## inne

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/health` | Health | publiczna (link z tokenem / logowanie) |

## kierowca

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/containers/{container_id}/driver-sms` | Sms History | admin, logistics, forwarder |
| POST | `/api/containers/{container_id}/driver-sms` | Send Sms Now | admin, logistics, forwarder |

## kolejka

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/analysis/forecast` | Prognoza rozładunków 4 tyg. w przód: kontenery/dzień vs limit + palety. | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/analysis/unloading` | Dzienna liczba kontenerów morskich/kolejowych per magazyn vs limity rozładunków. | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/calendar` | List Calendar | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| PUT | `/api/calendar` | Set Calendar Day | admin, logistics |
| GET | `/api/calendar/year` | Widok roczny kalendarza: liczba kontenerów per dzień awizacji × magazyn. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/changes/digest` | Co się zmieniło w kontenerach w ostatnich N godzinach — z audytu. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/changes/feed` | Dziennik zmian od początku dnia (czas PL) dla admin+logistyki. | admin, logistics |
| DELETE | `/api/containers` | Czyści kolejkę (tylko admin) — do resetu przed wgraniem nowej do testów. | admin |
| GET | `/api/containers` | List Containers | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/containers` | Create Container | admin, logistics |
| POST | `/api/containers/bulk/status` | Bulk Status | admin, logistics, warehouse |
| POST | `/api/containers/bulk/warehouse` | Bulk Warehouse | admin, logistics |
| GET | `/api/containers/counts` | Liczba aktywnych (niezrealizowanych) kontenerów per spółka — do kart zakładek. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/containers/export/xlsx` | Eksport przefiltrowanej kolejki do pliku Excel (.xlsx). | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/containers/fill-summary` | Zagregowane % wypełnienia dla listy kontenerów (kolumna w kolejce). | admin, logistics, forwarder, purchasing |
| POST | `/api/containers/import-po` | #42: dopisuje numery zamówień (order_numbers) do ISTNIEJĄCYCH kontenerów po | admin |
| GET | `/api/containers/plan/pending` | Kontenery czekające na potwierdzenie daty — lista dla modułu spedycji. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/containers/plan/send` | Wysyła propozycje dat do spedycji — zamraża je, oznacza jako oczekujące i wysyła | admin, logistics |
| GET | `/api/containers/to-forward` | Kolejka „do zlecenia": aktywne kontenery bez aktywnego TransportJob, z flagą | admin, logistics |
| GET | `/api/containers/transport-conflicts` | Ostrzeżenia kolejki: to samo zlecenie transportowe rozjeżdża się tego samego | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| DELETE | `/api/containers/{container_id}` | Usuwa pojedynczy kontener z kolejki (tylko admin). Uwaga: kolejka syncuje się | admin |
| GET | `/api/containers/{container_id}` | Get Container | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| PATCH | `/api/containers/{container_id}` | Update Container | admin, logistics |
| GET | `/api/containers/{container_id}/history` | Container History | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/containers/{container_id}/items` | Container Items | admin, logistics, warehouse, forwarder, purchasing, sales |
| PATCH | `/api/containers/{container_id}/needs-forwarding` | Set Needs Forwarding | admin, logistics |
| GET | `/api/containers/{container_id}/packing` | Wypełnienie kontenera 3D: pozycje zamówień × wymiary MARM ułożone packerem | admin, logistics, forwarder, purchasing |
| GET | `/api/containers/{container_id}/palletization` | #46: sekcja paletyzacji na karcie rozładunku — proxy do serwisu paletyzacji (best-effort). | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/containers/{container_id}/plan/confirm` | Potwierdzenie daty przez zalogowaną spedycję (portal). | admin, logistics, forwarder |
| GET | `/api/containers/{container_id}/sent-links` | Container Sent Links | admin, logistics, forwarder, purchasing |
| POST | `/api/containers/{container_id}/sent-links` | Add Sent Link | admin, logistics |
| POST | `/api/containers/{container_id}/special` | Flaga „specjalny" (wyróżnienie do śledzenia) — globalna, nie per-user jak gwiazdka; | admin, logistics |
| POST | `/api/containers/{container_id}/status` | Change Status | admin, logistics, warehouse |
| GET | `/api/containers/{container_id}/suggest-notify-date` | #50: propozycja daty awizacji — pierwszy dzień roboczy (kalendarz magazynu) | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/containers/{container_id}/warehouse` | Szybka zmiana magazynu rozładunku (menu kontekstowe w kolejce). | admin, logistics |
| POST | `/api/containers/{container_id}/watch` | Toggle gwiazdki — idempotentny (drugi POST zdejmuje obserwację). | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/limits` | List Limits | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| PUT | `/api/limits` | Set Limit | admin, logistics |
| GET | `/api/orders` | List Orders | admin, logistics, purchasing |
| POST | `/api/orders` | Create Order | admin, logistics |
| GET | `/api/orders/{order_id}` | Get Order | admin, logistics, purchasing |
| GET | `/api/queue` | Queue View | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| DELETE | `/api/sent-links/{link_id}` | Delete Sent Link | admin, logistics |
| GET | `/api/stats/dashboard` | Kafelki dashboardu + listy wymagające uwagi (w zakresie użytkownika). | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/stats/demurrage-risk` | Pomysł 10 PO: kontenery z ryzykiem kary za przestój i powodem (zakres jak pulpit). | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/stats/monthly` | Monthly Stats | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/stats/occupancy-forecast` | Suma kontenerów i palet z notify_date w każdym z najbliższych 4 tygodni. | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/stats/overview` | Overview | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/stats/transit-trend` | Średni czas transportu (ETD→ATD) zakończonych kontenerów per miesiąc ATD. | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/stats/value` | Value Panel | admin, logistics |
| GET | `/api/ui-config` | Drobna konfiguracja UI dla zalogowanych (ustawienia admina czytane przez front). | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/watch` | Watched Ids | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/watch/reasons` | Powody własnych obserwacji (tylko niepuste) — kolejka pokazuje je przy gwiazdce. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/zlecenia` | Zakłada zlecenie (Beta/Gamma): jedno zamówienie → N rekordów kontenerów w kolejce. | admin, logistics |

## mag1

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/mag1/{token}` | Mag1 Info | publiczna (link z tokenem / logowanie) |
| POST | `/api/mag1/{token}/prepared` | Mag1 Prepared | publiczna (link z tokenem / logowanie) |
| POST | `/api/mag1/{token}/shipped` | Mag1 Shipped | publiczna (link z tokenem / logowanie) |

## magazyn

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/containers/{container_id}/ramp-stage` | D9: etap rampy ustawia magazyn (drugi wymiar — ContainerStatus bez zmian). | admin, logistics, warehouse |
| GET | `/api/containers/{container_id}/unload-photos` | List Unload Photos | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/containers/{container_id}/unload-photos` | Upload Unload Photo | admin, logistics, warehouse |
| POST | `/api/containers/{container_id}/unload/start` | Unload Start | admin, logistics, warehouse |
| POST | `/api/containers/{container_id}/unload/stop` | Unload Stop | admin, logistics, warehouse |
| GET | `/api/gate` | Dzisiejsze spodziewane auta: kontener, nr rej., status przyjazdu/check-in. | admin, logistics, warehouse |
| POST | `/api/gate/{container_id}/checkin` | Check-in ochrony „Przyjechał": audyt + dzwonek do magazynu. Idempotentny w dniu. | admin, logistics, warehouse |
| POST | `/api/gate/{container_id}/delay` | Kierowca zadzwonił, że się spóźni — logistyka/magazyn wpisuje nową godzinę (zamiast | admin, logistics, warehouse |
| POST | `/api/unload-photos/{photo_id}/complaint` | Prefill draftu reklamacji z kontenerem i podpiętym zdjęciem z rozładunku. | admin, logistics, warehouse |
| GET | `/api/unload-photos/{photo_id}/download` | Download Unload Photo | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/warehouse/staffing` | Palety do rozładunku jutro/pojutrze ÷ palety/os./zmianę → sugerowana obsada. | admin, logistics, warehouse, purchasing |

## master-data

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/master-data/quality` | Raport jakości master data: problemy per reguła + wiek importów. | admin, logistics |

## materiały

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/materials` | List Materials | admin, logistics, purchasing |
| GET | `/api/materials/count` | Aktywne materiały — tyle, ile widzi lista i dopasowanie faktur. | admin, logistics, purchasing |
| POST | `/api/materials/import` | Import xlsx (szablon master daty: nagłówek 1- lub 2-wierszowy z bannerem poziomów). | admin |
| GET | `/api/materials/ml/stats` | Ml Stats | admin, logistics, purchasing |
| POST | `/api/materials/ml/train` | Trening modeli ML z bazy (materiały, zatwierdzone pozycje, teksty dokumentów). | admin |
| PATCH | `/api/materials/{material_id}` | Update Material | admin |
| PUT | `/api/materials/{material_id}/override` | Nadpisanie pól dla spółki; komplet pustych pól = usunięcie nadpisania. | admin |

## monitor

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/admin/logs/client-errors` | Client Errors | admin |
| GET | `/api/admin/logs/jobs` | Jobs | admin |
| GET | `/api/admin/logs/requests` | List Request Logs | admin |
| GET | `/api/admin/logs/traffic` | Traffic | admin |

## obecność

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| POST | `/api/presence` | Sygnał karty (co ~30 s i przy zmianie ekranu) → lista obecnych (z Tobą). | admin, logistics, purchasing, sales |
| POST | `/api/presence/leave` | Wylogowanie / zamknięcie karty — znikasz od razu, nie po 15 min. | admin, logistics, purchasing, sales |

## obserwowanie

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/containers/{container_id}/watchers` | Container Watchers | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/tracking/vessels/{vessel_id}/watch` | Toggle gwiazdki statku — jak kontener: drugi POST zdejmuje obserwację. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/tracking/vessels/{vessel_id}/watchers` | Vessel Watchers | admin, logistics, warehouse, forwarder, customs, purchasing, sales |

## portal

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| PUT | `/api/containers/{container_id}/customer` | Set Container Customer | admin, logistics |
| GET | `/api/customers` | List Customers | admin, logistics |
| POST | `/api/customers` | Create Customer | admin, logistics |
| DELETE | `/api/customers/{customer_id}` | Delete Customer | admin, logistics |
| PATCH | `/api/customers/{customer_id}` | Update Customer | admin, logistics |
| GET | `/api/public/branding` | Branding stron publicznych — z konfiguracji, bez hardkodu spółki. | publiczna (link z tokenem / logowanie) |

## powiadomienia

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/notifications` | List Notifications | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/notifications/feed` | Aktualności: najnowsze pierwsze, po `limit` z „załaduj starsze” (before_id); | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/notifications/mutes` | Moje wyciszone kontenery (do kiedy) — tylko w zakresie użytkownika. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/notifications/mutes` | „Nie przypominaj przez 1 / 3 / 7 dni” — tylko własne powiadomienia, tylko kontener w zakresie. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| DELETE | `/api/notifications/mutes/{container_id}` | Remove Mute | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/notifications/read` | Mark Read | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/notifications/rules` | Matryca reguł: znane kindy/role/kanały + nadpisania (brak wpisu = włączone). | admin |
| PUT | `/api/notifications/rules` | Zapis matrycy: pełna wymiana nadpisań. Wpisy enabled=True (=domyślne) | admin |
| POST | `/api/notifications/unread` | „Oznacz jako nieprzeczytaną” w panelu czytania Aktualności. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/notifications/unread-count` | Unread Count | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/notifications/{notification_id}/thread` | Oś zdarzeń wątku (ten sam kontener albo statek) — panel czytania. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |

## profil dostawcy

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/suppliers/{supplier_id}/doc-profile` | Get Profile | admin, logistics, purchasing |
| PUT | `/api/suppliers/{supplier_id}/doc-profile` | Put Profile | admin |
| POST | `/api/suppliers/{supplier_id}/doc-profile/samples` | Upload Sample | admin |
| DELETE | `/api/suppliers/{supplier_id}/doc-profile/samples/{sample_id}` | Delete Sample | admin |
| GET | `/api/suppliers/{supplier_id}/doc-profile/samples/{sample_id}/preview` | Tabela z próbki (CI albo PL) do mapowania kolumn + podział stron. | admin, logistics, purchasing |
| POST | `/api/suppliers/{supplier_id}/doc-profile/test` | Test NIEZAPISANEGO stanu kreatora na wszystkich próbkach; wynik zapisany w próbkach | admin |
| PUT | `/api/suppliers/{supplier_id}/required-docs` | Wymagane dokumenty dostawcy (spec 2026-10-06 decyzja 16) — czytają je kafelki i ostrzeżenie | admin |

## purchase-orders

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/purchase-orders` | Zamówienia zakupowe. Domyślnie tylko NIEPOWIĄZANE z kontenerem | admin, logistics, purchasing |
| DELETE | `/api/purchase-orders/{po_id}` | Usunięcie zamówienia zakupowego (tylko admin, w granicach spółek usera). | admin |

## reklamacje

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/complaint-photos/{photo_id}/download` | Download Photo | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/complaints` | List Complaints | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/complaints` | Create Complaint | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/complaints/stats` | Rejestr szkód (W11 #68/#71): % kontenerów z reklamacją per dostawca i armator | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/complaints/{complaint_id}` | Get Complaint | admin, logistics, warehouse, forwarder, customs, purchasing |
| PATCH | `/api/complaints/{complaint_id}` | Update Complaint | admin, logistics, warehouse |
| GET | `/api/complaints/{complaint_id}/letter` | Complaint Letter | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/complaints/{complaint_id}/photos` | Upload Photo | admin, logistics, warehouse |
| POST | `/api/complaints/{complaint_id}/report` | Report Complaint | admin, logistics, warehouse |
| POST | `/api/complaints/{complaint_id}/send` | Send Complaint | admin, logistics |
| POST | `/api/complaints/{complaint_id}/status` | Change Complaint Status | admin, logistics |
| GET | `/api/problem-types` | List Problem Types | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/problem-types` | Create Problem Type | admin |
| PATCH | `/api/problem-types/{type_id}` | Update Problem Type | admin |
| GET | `/api/settings` | Read Settings | admin |
| PUT | `/api/settings` | Write Settings | admin |

## specjalna troska

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/customer-orders` | List Customer Orders | admin, logistics, sales |
| POST | `/api/customer-orders` | Create Customer Order | admin, logistics |
| GET | `/api/customer-orders/responsibles` | Lekka lista osób do pola „Odpowiedzialny” (audyt UI S10): tylko id + imię | admin, logistics |
| DELETE | `/api/customer-orders/{order_id}` | Delete Customer Order | admin, logistics |
| PATCH | `/api/customer-orders/{order_id}` | Update Customer Order | admin, logistics |

## spedycja

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| DELETE | `/api/attachments/{attachment_id}` | Pomyłka przy wgraniu: partnerzy tylko własne pliki; po wysłaniu do agencji / po odprawie | admin, logistics, forwarder, customs, purchasing |
| GET | `/api/attachments/{attachment_id}/download` | Download Attachment | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/containers/{container_id}/attachments` | List Attachments | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/containers/{container_id}/attachments` | Upload Attachment | admin, logistics, forwarder, customs, purchasing |
| DELETE | `/api/containers/{container_id}/attachments/{attachment_id}/link` | Odepnij wspólny plik od kontenera powiązanego (plik zostaje u właściciela). | admin, logistics, forwarder, customs, purchasing |
| POST | `/api/containers/{container_id}/attachments/{attachment_id}/link` | Dokument zbiorczy (decyzja 24): ten sam plik także w innym kontenerze tej samej spółki. | admin, logistics, forwarder, customs, purchasing |
| PATCH | `/api/containers/{container_id}/customs` | Update Customs | admin, logistics |
| PATCH | `/api/containers/{container_id}/driver` | Update Driver | admin, logistics, forwarder |
| GET | `/api/containers/{container_id}/messages` | List Messages | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/containers/{container_id}/messages` | Create Message | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/forwarding/queue-email` | Send Queue Email | admin, logistics |
| GET | `/api/freight-invoices` | List Freight Invoices | admin, logistics, purchasing |
| POST | `/api/freight-invoices` | Create Freight Invoice | admin, logistics |
| DELETE | `/api/freight-invoices/{invoice_id}` | Delete Freight Invoice | admin, logistics |
| POST | `/api/freight-invoices/{invoice_id}/approve` | Zatwierdzenie do zapłaty (rozdzielenie obowiązków — zatwierdza admin, nie twórca). | admin |
| GET | `/api/freight-invoices/{invoice_id}/download` | Download Freight Invoice | admin, logistics, purchasing |
| POST | `/api/freight-invoices/{invoice_id}/reject` | Odrzucenie faktury (z powodem); wraca do poprawy — twórca może zgłosić ponownie. | admin |
| POST | `/api/freight-invoices/{invoice_id}/submit` | Zgłoszenie faktury do akceptacji (twórca / logistyka). | admin, logistics |
| GET | `/api/transport-orders` | List Transport Orders | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/transport-orders` | Create Transport Order | admin, logistics |
| GET | `/api/transport-orders/kpi` | KPI spedycji (W9): zlecenia per spedytor, rozkład statusów, średni czas | admin, logistics, warehouse, forwarder, customs, purchasing |
| POST | `/api/transport-orders/{order_id}/status` | Change Order Status | admin, logistics, warehouse, forwarder, customs, purchasing |

## system

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/admin/auth-log` | Auth Log | admin |
| GET | `/api/admin/blocked-ips` | List Blocked Ips | admin |
| POST | `/api/admin/blocked-ips` | Block Ip | admin |
| DELETE | `/api/admin/blocked-ips/{blocked_id}` | Unblock Ip | admin |
| GET | `/api/admin/health/deep` | Te same kontrole ze szczegółami — admin sprawdza, dlaczego monitor świeci na czerwono. | admin |
| POST | `/api/admin/impersonate` | Impersonate | admin |
| GET | `/api/admin/integrations` | Stan integracji zewnętrznych (W12): skonfigurowana/wyłączona + ostatni sygnał. | admin |
| GET | `/api/admin/monitor` | Server Monitor | admin |
| GET | `/api/admin/system` | System Status | admin |
| POST | `/api/admin/system/verify-backup` | W14 #47: ręczne uruchomienie weryfikacji backupu (przycisk w panelu System). | admin |
| POST | `/api/client-error` | Client Error | publiczna (link z tokenem / logowanie) |
| GET | `/api/health/deep` | Dla monitora z zewnątrz: kod 200/503 i sam status — bez szczegółów dla anonimów. | publiczna (link z tokenem / logowanie) |
| POST | `/api/users/{user_id}/2fa/disable` | Wyłączenie 2FA tylko przez INNEGO admina (zgubiony telefon), z audytem. | admin |
| GET | `/api/users/{user_id}/sessions` | User Sessions | admin |
| DELETE | `/api/users/{user_id}/sessions/{session_id}` | Revoke User Session | admin |

## słowniki

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/audit/{entity_type}` | Historia zmian CAŁEGO słownika (#19) — paginowana, filtr po polu/użytkowniku. | admin, logistics |
| GET | `/api/audit/{entity_type}/{entity_id}` | Entity History | admin, logistics |
| GET | `/api/carriers` | List Carriers | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/carriers` | Create Carrier | admin |
| DELETE | `/api/carriers/{carrier_id}` | Delete Carrier | admin |
| PATCH | `/api/carriers/{carrier_id}` | Update Carrier | admin |
| POST | `/api/carriers/{carrier_id}/merge` | Merge Carrier | admin |
| GET | `/api/container-ports` | Słownik portów kontenerowych (master data globalne, read-only). | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| DELETE | `/api/container-ports/{port_id}` | Delete Container Port | admin |
| GET | `/api/container-types` | List Container Types | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/container-types` | Create Container Type | admin |
| GET | `/api/forwarders` | List Forwarders | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/forwarders` | Create Forwarder | admin |
| DELETE | `/api/forwarders/{forwarder_id}` | Delete Forwarder | admin |
| PATCH | `/api/forwarders/{forwarder_id}` | Update Forwarder | admin |
| POST | `/api/forwarders/{forwarder_id}/merge` | Merge Forwarder | admin |
| GET | `/api/fx` | Przelicza kwotę na PLN/EUR/USD wg kursów NBP (best-effort — available=False gdy brak). | admin, logistics, warehouse, forwarder, customs, purchasing |
| GET | `/api/material-units` | Jednostki materiałów z MARM (master data globalne, read-only) — wyszukiwarka | admin, logistics, warehouse, forwarder, customs, purchasing |
| DELETE | `/api/material-units/{unit_id}` | Delete Material Unit | admin |
| GET | `/api/ports` | List Ports | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/ports` | Create Port | admin |
| DELETE | `/api/ports/{port_id}` | Delete Port | admin |
| PATCH | `/api/ports/{port_id}` | Update Port | admin |
| POST | `/api/ports/{port_id}/merge` | Merge Port | admin |
| GET | `/api/supplier-contacts` | List Supplier Contacts | admin, logistics, warehouse, customs, purchasing |
| POST | `/api/supplier-contacts` | Create Supplier Contact | admin, logistics |
| GET | `/api/suppliers` | List Suppliers | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/suppliers` | Create Supplier | admin |
| DELETE | `/api/suppliers/aliases/{alias_id}` | Usuwa alias (przyszłe importy tej nazwy wrócą na listę); kontenery już przypięte zostają. | admin, logistics |
| GET | `/api/suppliers/resolve` | „Do rozstrzygnięcia" (dry-run): grupy tego samego kodu SAP + kartoteka bez kodu SAP. | admin |
| POST | `/api/suppliers/resolve/apply` | Scala wszystkie grupy tego samego kodu SAP w jednej transakcji (audyt per scalenie). | admin |
| GET | `/api/suppliers/resolve/orphans` | Podgląd kopii bez żadnych powiązań (decyzja usera #2, 2026-09-25) — nic nie zmienia. | admin |
| POST | `/api/suppliers/resolve/orphans/delete` | Kasuje wszystkie kopie bez powiązań w jednej transakcji (audyt zbiorczy). | admin |
| GET | `/api/suppliers/unmapped` | Nazwy z pliku bez dostawcy w słowniku (w zakresie usera), najczęstsze najpierw. | admin, logistics |
| DELETE | `/api/suppliers/{supplier_id}` | Delete Supplier | admin |
| PATCH | `/api/suppliers/{supplier_id}` | Update Supplier | admin |
| GET | `/api/suppliers/{supplier_id}/aliases` | List Aliases | admin, logistics |
| POST | `/api/suppliers/{supplier_id}/aliases` | Alias nazwy → dostawca w spółce pliku + przypięcie kontenerów tej spółki z tą nazwą | admin, logistics |
| POST | `/api/suppliers/{supplier_id}/merge` | Merge Supplier | admin |
| GET | `/api/suppliers/{supplier_id}/stats` | #39: KPI karty dostawcy — liczone w zakresie usera (scope_containers), nie | admin, logistics, forwarder, purchasing |
| GET | `/api/warehouses` | List Warehouses | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/warehouses` | Create Warehouse | admin |
| DELETE | `/api/warehouses/{warehouse_id}` | Delete Warehouse | admin |
| PATCH | `/api/warehouses/{warehouse_id}` | Update Warehouse | admin |

## tracking

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/containers/{container_id}/events` | Container Events | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/containers/{container_id}/timeline` | Container Timeline | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/tracking/congestion` | Trend kongestii per port (ostatnie 14 dni) do mini-wykresu przy chipie portu. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/tracking/map` | Punkty na mapę: ostatnie znane położenie każdego ŚLEDZONEGO kontenera. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/tracking/vessels` | Pozycje AIS statków z aktywnej kolejki + trasa przebyta, spółki i pilność. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/tracking/vessels/{vessel_id}/cargo` | Kontenery usera na pokładzie + pozycje zamówień (akordeon karty statku). | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/tracking/vessels/{vessel_id}/photo` | Vessel Photo | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/tracking/vessels/{vessel_id}/photo` | Upload Vessel Photo | admin |
| POST | `/api/tracking/vessels/{vessel_id}/photo/fetch` | Auto-pobranie miniatury z Wikimedia Commons (jedyne zbadane źródło bez klucza | admin |
| GET | `/api/tracking/weather` | Wiatr i fala w pozycjach śledzonych statków — przycięte do statków | admin, logistics, warehouse, forwarder, customs, purchasing, sales |

## wiedza

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/knowledge/bulletins` | Edytorzy widzą wszystkie noty swojej spółki/grupy; pozostali — adresowane do swojej roli. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/knowledge/bulletins` | Create Bulletin | admin, logistics |
| GET | `/api/knowledge/bulletins/unread` | Noty adresowane do roli usera bez jego potwierdzenia — zasila baner. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| POST | `/api/knowledge/bulletins/{bulletin_id}/ack` | „Przeczytałem" — idempotentne, pierwszy read_at zostaje. | admin, logistics, warehouse, forwarder, customs, purchasing, sales |
| GET | `/api/knowledge/bulletins/{bulletin_id}/acks` | Kto przeczytał / kto nie — wszyscy aktywni adresaci noty z read_at lub bez. | admin, logistics |
| GET | `/api/knowledge/notes` | List Notes | admin, logistics, warehouse, purchasing, sales |
| POST | `/api/knowledge/notes` | Create Note | admin, logistics |
| DELETE | `/api/knowledge/notes/{note_id}` | Soft-delete: pinezka znika z paneli, historia i audyt zostają. | admin, logistics |
| PATCH | `/api/knowledge/notes/{note_id}` | Update Note | admin, logistics |
| GET | `/api/knowledge/topics` | List Topics | admin, logistics, warehouse, purchasing, sales |
| POST | `/api/knowledge/topics` | Create Topic | admin, logistics, warehouse, purchasing |
| PATCH | `/api/knowledge/topics/{topic_id}/status` | Set Topic Status | admin, logistics |
| POST | `/api/knowledge/topics/{topic_id}/vote` | +1 na temat; idempotentne — ponowny głos niczego nie dubluje. | admin, logistics, warehouse, purchasing |

## wyceny

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/stats/cost-report` | Raport kosztów transportu na żądanie (Q98): suma wygranych ofert per miesiąc | admin, logistics |
| GET | `/api/stats/forwarders` | Raport wydajności spedytorów: ile zapytań, odpowiedzi, wygranych, brak sprzętu, | admin, logistics |
| GET | `/api/stats/transport-jobs.csv` | Eksport zleceń wyceny do CSV (Q86). | admin, logistics |
| GET | `/api/transport-jobs` | List Jobs | admin, logistics, warehouse, forwarder, customs |
| POST | `/api/transport-jobs` | Create Job | admin, logistics |
| GET | `/api/transport-jobs/{job_id}` | Get Job | admin, logistics, warehouse, forwarder, customs |
| PATCH | `/api/transport-jobs/{job_id}` | Edycja terminu/SCFI (przed rozstrzygnięciem), danych odbioru/dostawy i numeru | admin, logistics |
| POST | `/api/transport-jobs/{job_id}/agent` | Wygrywająca spedycja podaje dane agenta (imię/nazwisko, telefon, firma) | admin, logistics, warehouse, forwarder, customs |
| POST | `/api/transport-jobs/{job_id}/cancel` | Anulowanie zlecenia z obowiązkowym powodem — także zlecenia już przydzielonego | admin, logistics |
| POST | `/api/transport-jobs/{job_id}/choose` | Wybór zwycięskiej oferty — pozostałe zostają odrzucone; powiadomienia do spedycji. | admin, logistics |
| POST | `/api/transport-jobs/{job_id}/price-change` | Q55: każda zaproszona spedycja może zgłosić pilną zmianę ceny; zmiana czeka na | admin, logistics, warehouse, forwarder, customs |
| POST | `/api/transport-jobs/{job_id}/quote` | Spedytor podaje cenę dla swojego zaproszenia. | admin, logistics, warehouse, forwarder, customs |
| POST | `/api/transport-jobs/{job_id}/quotes/{quote_id}/approve-price` | Q56: logistyka akceptuje zgłoszoną zmianę ceny — nowa cena zastępuje ofertę. | admin, logistics |
| GET | `/api/transport-jobs/{job_id}/quotes/{quote_id}/history` | Historia wersji oferty (Q47) — logistyka dla dowolnej oferty, spedytor tylko własnej. | admin, logistics, warehouse, forwarder, customs |
| POST | `/api/transport-jobs/{job_id}/reopen` | Wznowienie anulowanego zlecenia (Q58) — wraca do szkicu z tymi samymi kontenerami | admin, logistics |
| POST | `/api/transport-jobs/{job_id}/send` | Publikacja zlecenia — od teraz zaproszone spedycje je widzą i mogą wyceniać. | admin, logistics |

## wyszukiwarka

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/search/suggest` | q > 50 znaków jest PRZYCINANE (nie 422) — pole ma maxlength=50, a wklejka z innego | admin, logistics, warehouse, forwarder, customs, purchasing, sales |

## wywolania-mag1

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/pallet-calls` | List Calls | admin, logistics, warehouse, purchasing |
| POST | `/api/pallet-calls` | Create | admin, logistics |
| GET | `/api/pallet-calls/analysis` | Analysis | admin, logistics, warehouse, purchasing |
| GET | `/api/pallet-calls/hu-inventory` | #65 Inwentaryzacja HU: rozjazdy HU wg PBI (stan MAG-1) vs HU wywołane. | admin, logistics, warehouse, purchasing |
| POST | `/api/pallet-calls/powerbi/connect` | Rozpoczyna device-code; zwraca kod dla użytkownika. Dokończenie w tle. | admin |
| GET | `/api/pallet-calls/powerbi/status` | Status integracji Power BI dla gatingu UI. | admin, logistics, warehouse, purchasing |
| GET | `/api/pallet-calls/{call_id}` | Get One | admin, logistics, warehouse, purchasing |
| PATCH | `/api/pallet-calls/{call_id}` | Update | admin, logistics |
| POST | `/api/pallet-calls/{call_id}/cancel` | Cancel | admin, logistics |
| POST | `/api/pallet-calls/{call_id}/confirm` | Confirm | admin, logistics |
| POST | `/api/pallet-calls/{call_id}/deliver` | Palety przywiezione — przestają być odejmowane z sugestii (wychodzą z 'w drodze'). | admin, logistics |
| POST | `/api/pallet-calls/{call_id}/prepared` | Magazyn MAG-1 (konto z rolą warehouse) potwierdza przygotowanie — zamiast linku z maila | admin, logistics, warehouse |
| POST | `/api/pallet-calls/{call_id}/send` | Send | admin, logistics |
| POST | `/api/pallet-calls/{call_id}/shipped` | Shipped | admin, logistics, warehouse |
| GET | `/api/pallet-calls/{call_id}/xlsx` | Download Xlsx | admin, logistics, warehouse, purchasing |
| GET | `/api/paz` | List Paz | admin, logistics, warehouse, purchasing |
| POST | `/api/paz` | Upsert Paz | admin |
| POST | `/api/paz/import` | Import z csv/xlsx — kolumny 'produkt' i 'sztuk_na_palete' (po nagłówku). | admin |
| DELETE | `/api/paz/{paz_id}` | Delete Paz | admin |
| GET | `/api/stock-targets` | List Targets | admin, logistics, warehouse, purchasing |
| POST | `/api/stock-targets` | Upsert Target | admin |
| DELETE | `/api/stock-targets/{target_id}` | Delete Target | admin |

## wzory agencji

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/agency-templates` | List Templates | admin, logistics |
| PUT | `/api/agency-templates/{key}` | Update Template | admin, logistics |
| GET | `/api/agency-templates/{key}/sample` | Download Sample | admin, logistics |
| POST | `/api/agency-templates/{key}/sample` | Nowy wzór od agencji (.xlsx): nagłówki z 1. wiersza = układ kolumn, 2. wiersz = przykłady. | admin, logistics |

## zakupy

| Metoda | Ścieżka | Opis | Kto ma dostęp |
|---|---|---|---|
| GET | `/api/containers/{cid}/order-lines` | 3-way per pozycja: zamówiono (OrderItem) vs przyjęto (GoodsReceiptLine) vs | admin, logistics, warehouse, forwarder, purchasing, sales |
| GET | `/api/containers/{cid}/receipts` | List Receipts | admin, logistics, warehouse, forwarder, purchasing, sales |
| PUT | `/api/containers/{cid}/receipts` | Zapis przyjęcia dla pozycji (upsert po order_number+position w tym kontenerze). | admin, logistics, warehouse, purchasing |
| DELETE | `/api/containers/{cid}/receipts/{receipt_id}` | Delete Receipt | admin, logistics, warehouse, purchasing |
| PUT | `/api/purchasing/containers/{container_id}/status` | Zmiana statusu zakupowego. Zakres firmowy pilnuje get_scoped (403/404 poza spółką). | admin, logistics, purchasing |
| GET | `/api/supplier-material-maps` | Mapowania w zasięgu użytkownika; opcjonalny filtr spółki/dostawcy/frazy (kod lub ref). | admin, logistics, warehouse, purchasing |
| POST | `/api/supplier-material-maps` | Nowe mapowanie; ten sam (spółka, dostawca, kod) = aktualizacja ref_code (upsert). | admin, logistics, purchasing |
| DELETE | `/api/supplier-material-maps/{map_id}` | Usunięcie mapowania (w granicach spółki wpisu). | admin, logistics, purchasing |
| PATCH | `/api/supplier-material-maps/{map_id}` | Zmiana ref_code / kodu / notatki (w granicach spółki wpisu). | admin, logistics, purchasing |
