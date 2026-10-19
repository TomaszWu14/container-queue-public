# Macierz śledzenia: wymaganie → historyjka → test → PR

Wersja 0.1 (2026-10-16), [BA]. Utrzymywana przy każdym odbiorze BA (krok 6 procesu). Testy backendu
w `backend/tests/`, frontendu w `frontend/src/`. Kolumna PR: numer PR w tym repozytorium; wymagania rdzenia
wdrożono przed uruchomieniem procesu w repozytorium prywatnym — tam numery PR nie są publicznie dostępne.

## Wymagania rdzenia (wdrożone przed procesem)

| Wymaganie | Odpowiednik w `05` | Historyjka | Test | PR |
|---|---|---|---|---|
| FR-001 numer ISO 6346 | W-01 | przed procesem | `test_api.py::test_iso6346_validation`, `test_iso6346_remainder10.py` | repo prywatne |
| FR-002 unikalność numeru wśród aktywnych | W-02 | przed procesem | `test_import_repeat_number.py` | repo prywatne |
| FR-003 10 statusów, cofanie z notatką | W-03 | przed procesem | `test_status_flow.py` | repo prywatne |
| FR-004 magazyn tylko DOSTARCZONY | W-04 | przed procesem | `test_api.py::test_warehouse_role_limited_to_unload_confirmation` | repo prywatne |
| FR-005 status z odprawy, tylko do przodu | W-05 | przed procesem | `test_status_from_customs.py` | repo prywatne |
| FR-006 historia każdej zmiany | W-06 | przed procesem; US-003 (wersjonowanie) | `test_audit_history.py`, `test_audit_coverage.py` | repo prywatne |
| FR-007 kto zmienia status odprawy | W-07 | przed procesem | `test_customs.py`, `test_document_tiles.py::test_sad_upload_by_forwarder_keeps_customs_status`; **brak testu 403 dla spedytora** | repo prywatne |
| FR-008 cofnięcie odprawy wyjątkiem | W-08 | przed procesem | `test_customs.py` | repo prywatne |
| FR-009 wysyłka do agencji ostrzega o brakach ([spec](spec/WYSYLKA-DOKUMENTOW-DO-AGENCJI.md) AK-01…AK-20) | W-09 | przed procesem | `test_customs.py`, `test_w5_documents.py`, `test_invoice_agency_mail.py`, `sendDocsPreview.dom.test.tsx`; **brak testu AK-19, AK-20** | repo prywatne |
| FR-010 braki dokumentów nie blokują statusu | W-10 | przed procesem | `test_required_docs.py` | repo prywatne |
| FR-011 wymagane dokumenty wg etapu | W-11 | przed procesem | `test_document_tiles.py` | repo prywatne |
| FR-012 bramka numeru w PDF | W-12 | przed procesem | `test_document_gate.py` | repo prywatne |
| FR-013 SAD przesuwa odprawę | W-13 | przed procesem | `test_document_tiles.py` | repo prywatne |
| FR-014 propozycja daty ETA + 4 | W-14 | przed procesem; US-020 | `test_planning.py` | repo prywatne |
| FR-015 uzgodniona data nie zmienia się sama | W-15 | przed procesem; US-017 | `test_planning_confirm.py` | repo prywatne |
| FR-016 limit dzienny ostrzega | W-16 | przed procesem | `test_api.py::test_queue_limits_and_free_days` | repo prywatne |
| FR-017 dni wolne kraju magazynu | W-17 | przed procesem; US-016 | `test_holidays_snapshot.py` | repo prywatne |
| FR-018 sloty z pojemnością | W-18 | przed procesem | `test_avizo_slots.py` | repo prywatne |
| FR-019 jednorazowe linki awizacji | W-19 | przed procesem | `test_avizo_tokens.py` | repo prywatne |
| FR-020 odpowiedź spedytora po decyzji logistyki | W-20 | przed procesem; US-009 | `test_avizo_workflow.py` | repo prywatne |
| FR-021 publiczny formularz chroniony | W-21 | przed procesem; US-005 | `test_avizo_public.py` | repo prywatne |
| FR-022 spółka widzi swoje | W-22 | przed procesem; US-011 | `test_isolation.py`, `test_idor_containers.py` | repo prywatne |
| FR-023 partner widzi zlecone | W-23 | przed procesem; US-011 | `test_partner_company_scope.py`, `test_deps_container_access.py` | repo prywatne |
| FR-024 role widzą tylko potrzebne pola | W-24 | przed procesem | `test_forwarder_no_customs.py` | repo prywatne |
| FR-025 import nie cofa danych | W-25 | przed procesem | `test_sync_status_forward_only.py` | repo prywatne |
| FR-026 konflikt Excel/aplikacja: nowsza zmiana | W-26 | przed procesem | `test_sync_keeps_app_changes.py` | repo prywatne |
| FR-027 dane kierowców usuwane po 90 dniach | W-27 | przed procesem | `test_gdpr_driver_copies.py`, `test_gdpr_driver_no_avizo.py` | repo prywatne |
| FR-028 alert demurrage | W-28 | przed procesem | `test_demurrage_batch.py` | repo prywatne |

Wymagania niefunkcjonalne i bezpieczeństwa (NFR/SR) są śledzone przez historyjki niżej i przez
`../bezpieczenstwo/RYZYKA.md` (kolumna „Historyjka”).

## Backlog (proces zespołowy)

| Historyjka | Wymagania / ryzyka | Test (planowany) | PR | Stan |
|---|---|---|---|---|
| US-001 prod wymaga PostgreSQL | NFR-011, SR-009, R-04 | `test_config_failfast.py` (12 przypadków), `test_prod_without_https.py` | #18 | wdrożone (zmienna w Coolify: Z-007) |
| US-002 osobny klucz szyfrowania | SR-009, R-05 | `test_config_failfast.py`, testy `crypto` | — | do akceptacji PO |
| US-003 ochrona przed cichym nadpisaniem | FR-006, NFR-013, R-02, ADR-0003 | `test_status_lost_update.py`, `test_container_lost_update.py`, `status.guard.dom.test.tsx`, `transportOrders.dom.test.tsx` | #18 | wdrożone |
| US-004 załączniki po zawartości | SR-007, R-03 | `test_file_signatures.py` (31 przypadków) | #28 | wdrożone |
| US-005 ochrona tras publicznych | FR-021, SR-002, R-06 | `test_public_routes_guard.py` (4), `test_mag1_confirm.py` | #30 | wdrożone |
| US-006 bezpieczny XML, ZIP | SR-006, R-07 | `test_imports_malicious.py` (5), `test_sad_xml.py`, `test_archive_upload.py` | #30 | wdrożone |
| US-007 bramki CI | SR-013, R-08 | przebieg `security.yml`, `test_runtime_versions.py::test_pre_commit_tools_match_ci` | #18, #33, #34 | wdrożone |
| US-008 `csv_safe` | SR-006, B-002 | `test_exports.py::test_csv_safe*`, `csv.export.dom.test.ts` (US-008) | PR po #34 | zrealizowane, czeka na merge |
| US-009 awizacja bez fałszywego sukcesu | FR-020, NFR-007, P-01 | `AvizoFormPage.dom.test.tsx`, `AvizoDriverFormPage.dom.test.tsx`, `test_avizo_tokens.py` | #18 | wdrożone |
| US-010 dokumentacja po audycie | — | — | #18 (`SECURITY.md`) | częściowo |
| US-011 strażnik izolacji | FR-022…024, SR-005, R-01, ADR-0006 | `test_isolation_guard.py` (4) | #32 | wdrożone |
| US-012 RODO 1.0 | SR-011, R-09 | — | — | czeka na Z-009 |
| US-013 kopia off-site | NFR-002, SR-014, R-10 | `test_backup_offsite.py` (4 testy), `test_backup_scripts.py`; ćwiczenie odtworzenia po włączeniu | #28 | kod gotowy; włączenie w Coolify po stronie PO |
| US-014 mierniki (+ panel, pomysł 6) | M-1…M-7 | — | — | czeka na Z-004 |
| US-015 jedna wersja Python/Node | NFR-011 | `test_runtime_versions.py` (4) | #31 | wdrożone |
| US-016 Portugalia: telefon, kraj magazynu | FR-017, P-05, P-06, Z-022 | `test_phones_portugal.py` (13) | #29 | wdrożone |
| US-017 „Wyślij plan” wysyła mail | FR-015, FR-020, P-09 | `test_plan_mail.py` (4), `BulkActionBar.plan.dom.test.tsx` (3) | #28 | wdrożone |
| US-018 testy ekranów | TEST-007 | `AuthPages.dom.test.tsx` (7), `ClearQueueModal.dom.test.tsx` (3), `ImportModal.dom.test.tsx` (4) | #30 | wdrożone |
| US-019 2FA adminów | SR-004, E-01 | — | — | czeka na Z-008 |
| US-027 demo pokazuje cały proces | FR-005, FR-009…011, FR-019, FR-020, FR-028 | `test_seed_demo_process.py` (5 testów), `test_demo_mode.py` | #18 | wdrożone |
| US-028 konta demo per rola | FR-022…FR-024, E-05 | `test_seed_demo_process.py::test_role_accounts_see_own_scope_and_cannot_write` | #18 | wdrożone |
| US-029 ograniczenia widoków demo | E-05, R-12 | `test_demo_limits.py` (17 przypadków), `demoLimits.dom.test.tsx`, `ProfilePage.demo.dom.test.tsx` | #27 | wdrożone |
| US-030 skaner QR na bramie | Z-021 (brama #60) | `GateScanner.dom.test.tsx` (6), `gateScan.test.ts` (3) | #28 | wdrożone |
| US-031 testy wysyłki i 2FA | TEST-007, FR-015, SEC-006 | `AvizoSendModal.dom.test.tsx` (2), `QueueEmailModal.dom.test.tsx` (2), `AvizoProposeForm.dom.test.tsx` (2), `Enroll2FAPage.dom.test.tsx` (3) | #36 | wdrożone |
| US-032/033 ekran Automatyzacje i pilnowanie automatów | FR-015, OBS-009, Z-023 | `test_automations.py` (5), `AutomationsPage.dom.test.tsx` (3) | #37 | wdrożone |
| US-034 licznik oszczędności per automat | Z-020, Z-024 | `test_automations.py` (4), `AutomationsPage.dom.test.tsx` (2), `AutomationMinutesModal.dom.test.tsx` (1) | #38 | wdrożone |
| US-035 zdarzenia do n8n widoczne i testowalne | FR-020, Z-023 | `test_automations.py` (3), `test_automation.py` (3), `AutomationsPage.dom.test.tsx` (1) | #39 | wdrożone |
| US-036 kreator reguł bez kodu | Z-026, FR-015 | `test_automation_rules.py` (6), `AutomationRulesPanel.dom.test.tsx` (3) | #39 | wdrożone |
| US-037 jakość odczytu faktur przez AI | FR-015 | `test_ai_quality.py` (3), `AiQualityPanel.dom.test.tsx` (2) | #40 | wdrożone |
| US-038 przebieg procesu z historii statusów | FR-015, Z-027 | `test_process_mining.py` (4), `ProcessFlowPanel.dom.test.tsx` (3) | #42 | wdrożone |
| US-039 asystent bez modelu AI (demo) | FR-015, Z-028 | `test_assistant.py` (2 nowe + 4 zmienione), `assistant.dom.test.tsx` (1) | #45 | wdrożone |
| US-052 demo z danymi na ekranie Automatyzacje | US-032…037 | `test_seed_demo_automation.py` (2) | #46 | wdrożone |
| US-040 Symuluj dzień | Z-024, Z-029 | `test_demo_simulation.py` (2), `SimulateDayPanel.dom.test.tsx` (2) | #47 | wdrożone |
| US-046…050 dokumenty dla rekrutera, README EN | Z-020, Z-024, Z-025 | brak testu (dokumentacja; linki sprawdzone ręcznie) | #48 | wdrożone |
| US-041 przycisk w karcie Teams | FR-015 | `test_teams_mail_status.py` (1), `test_notifications_w4.py` (1 rozszerzony) | #49 | wdrożone |
| US-045 poradnik n8n w 15 minut | FR-020 | `test_n8n_workflows.py` (5) | #50 | wdrożone |
| US-042…044 Excel, Power BI, Power Automate (instrukcje) | ADR-0004 (bez zmian) | `test_m365_docs.py` (1) | #51 | wdrożone |
| US-053 strażnik automatów | OBS-009 | `test_automation_watchdog.py` (2) | #53 | wdrożone |
| US-054 tygodniowy raport automatów | Z-023, Z-024 | `test_automation_report.py` (2) | #54 | wdrożone |
| US-055 język startowy z przeglądarki | — | `i18n.detect.test.ts` (3) | #55 | wdrożone |
| US-056 E2E ekranu Automatyzacje w demo | US-032…040, US-055 | `e2e/demo/recruiter.spec.ts` (2 nowe × 2 urządzenia) | #56 | wdrożone |
| US-057 Lighthouse w CI | — | workflow `lighthouse.yml` (progi w `lighthouse-assert.mjs`) | #58 | wdrożone |
| US-058 zrzuty w README, realistyczna historia demo | US-038, US-052 | `test_seed_demo_automation.py` (1 nowy), zrzuty z `e2e/demo/recruiter.spec.ts` | #59 | wdrożone |
| US-059 włącz / wyłącz automat | Z-030 | `test_automation_switch.py` (2), `AutomationsPage.dom.test.tsx` (2) | #60 | wdrożone |
| US-060 pomyłki modelu do przeglądu | FR-015 | `test_ai_quality.py` (1), `AiMistakesTable.dom.test.tsx` (2) | #61 | wdrożone |
| US-061 wykres przepływu procesu | US-038 | `ProcessFlowChart.dom.test.tsx` (2), `test_process_mining.py` (rozszerzony), `test_seed_demo_automation.py` (1) | #62 | wdrożone |
| US-062 co jeśli statek się spóźni | Z-031 | `test_what_if.py` (2), `WhatIfPanel.dom.test.tsx` (2) | #63 | wdrożone |
| US-063 kanały reguły w kreatorze | US-036, Z-032 | `test_automation_rules.py` (1), `AutomationRulesPanel.dom.test.tsx` (1) | #64 | wdrożone |
| US-064 zero znanych błędów typów w modułach automatów | CODE-003 | `mypy_baseline.py` (CI), `test_backup_scripts.py` (1) | #65 | wdrożone |
| US-026 awaria integracji = komunikat | R-19, Z-033 | `test_integration_errors.py` (9) | #71 | wdrożone |
| US-065 „nie przypominaj” w dzwonku | Z-034 | `test_alert_mutes.py` (1), `notificationsBell.dom.test.tsx` (1) | #72 | wdrożone |
| US-066 historia zmian reguł i przywróć | US-036 | `test_automation_rules_history.py` (1), `AutomationRulesHistory.dom.test.tsx` (2) | #73 | wdrożone |
| US-065 „nie przypominaj” w dzwonku | Z-034 | `test_alert_mutes.py` (1), `notificationsBell.dom.test.tsx` (1) | — | czeka na merge |
| US-067 koszt kar w „co jeśli” | US-062, Z-035 | `test_what_if.py` (rozszerzony), `WhatIfPanel.dom.test.tsx` (rozszerzony) | #74 | wdrożone |
| US-022 ponawianie wysyłek | P-11, P-12, Z-036 | `test_delivery_retry.py` (4), `DeliveryRetryPanel.dom.test.tsx` (2) | #75 | wdrożone |
| US-066 historia zmian reguł i przywróć | US-036 | `test_automation_rules_history.py` (1), `AutomationRulesHistory.dom.test.tsx` (2) | — | czeka na merge |
| US-068 test reguły na 30 dniach | US-036, Z-037 | `test_automation_rules_backtest.py` (2), `RuleBacktest.dom.test.tsx` (2) | #76 | wdrożone |
| US-069 nagranie Automatyzacje w README | US-056 | `e2e/demo/recruiter.spec.ts` (rozszerzony) | #77 | wdrożone |
| US-024 archiwum notatek z pomysłami | AUDYT §2.6 pkt 8 | przegląd linków | — | czeka na merge |

## Zasady utrzymania

1. Nowa historyjka = nowy wiersz tutaj **w tym samym PR**, co jej analiza.
2. Scalony PR = numer w kolumnie PR i stan „wdrożone”; test w kolumnie Test musi istnieć i być zielony.
3. Wymaganie bez testu jest oznaczane **wprost** („brak testu”), nie pomijane — jak FR-007 wyżej.
