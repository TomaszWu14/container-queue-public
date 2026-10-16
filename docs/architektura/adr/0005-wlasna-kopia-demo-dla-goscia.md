# ADR-0005 · Własna kopia demo dla każdego odwiedzającego

- **Status:** proponowana — czeka na akceptację PO (pomysł 9, „wdrażaj wszystko” 2026-10-16)
- **Data:** 2026-10-16
- **Role:** [DEV] propozycja, [SEC] przegląd STRIDE niżej, [BA] pytania do PO na końcu

## Kontekst

Publiczne demo (`container.queue.twapp.pl`) to wspólne konto **tylko do odczytu** (US-029,
`demo_limits.py`). Gość nie może niczego zapisać, więc nie sprawdzi najważniejszego: zmiany statusu, planu,
awizacji. Pomysł 9: „Załóż swoją firmę w 2 minuty” — każdy dostaje własną, czystą kopię z danymi
pokazowymi i może klikać i zapisywać. Z-010: demo nigdy nie dostaje danych rzeczywistych.

## Rozważane opcje

1. **Osobna baza / kontener na gościa.** Pełna izolacja. Odrzucone: koszt i czas startu (sekundy–minuty),
   orkiestracja kontenerów na jednym serwerze Coolify.
2. **Osobny schemat PostgreSQL na gościa** (`search_path`). Dobra izolacja, ale migracje ×N schematów,
   pula połączeń per schemat, skomplikowane kopie zapasowe.
3. **Gość = nowa spółka w tej samej bazie demo.** Seed tworzy spółkę „Gość 7f3a…”, jej konta (logistyka,
   spedytor, agencja, magazyn) i ~60 kontenerów; izolację zapewnia istniejący mechanizm per spółka
   (`scope_containers`, `check_container_access`, D9). Sprzątanie: spółka gościa i jej dane kasowane po 24 h.
4. **Reset wspólnego demo co noc + zapis dla wszystkich.** Najtańsze. Odrzucone: goście widzą i psują
   sobie nawzajem dane, ryzyko treści obraźliwych widocznych dla następnych.

## Decyzja (proponowana)

Opcja 3 **wyłącznie na instancji demo** (`DEMO_SANDBOX=true`; produkcja odrzuca start z tą flagą):

- „Wypróbuj z zapisem” na stronie logowania demo → limit (bez CAPTCHA): maks. 3 kopie na IP na dobę,
  maks. 200 aktywnych kopii; potem komunikat „spróbuj później” (wspólne demo tylko do odczytu zostaje).
- Kopia żyje 24 h; nocne zadanie usuwa spółkę gościa kaskadowo (kontenery, pliki, audyt, konta).
- Konta gościa: losowy login, bez hasła — sesja w cookie; bez e-maili wychodzących (poczta, SMS, Teams
  wyłączone dla spółek gościnnych), bez wgrywania plików powyżej 2 MB.
- Słowniki wspólne (porty, typy dokumentów) tylko do odczytu dla gościa.

## Przegląd bezpieczeństwa [SEC] — STRIDE dla nowego przepływu F-SANDBOX

| Zagrożenie | Ryzyko | Kontrola w projekcie |
|---|---|---|
| **S** przejęcie kopii innego gościa | podgląd / zmiana cudzych zapisów | sesja = losowy token w cookie HttpOnly, SameSite; brak logowania hasłem do kont gości |
| **T** zmiana danych wspólnych (słowniki, konfiguracja) | psucie demo innym | gość nie ma roli admin; zapisy słowników i ustawień = 403 (rozszerzenie `demo_limits.py`); test |
| **R** nadużycia (treści obraźliwe) | wizerunek | dane gościa widzi tylko on; usunięcie po 24 h; log IP + czas założenia (7 dni) |
| **I** wyciek między gośćmi | **wysokie** | ta sama izolacja per spółka co produkcja (D9) — test „gość A nie widzi B” na każdej trasie z `permissions.yaml`; brak danych rzeczywistych (Z-010) |
| **D** zalewanie kopiami / dysku plikami | **wysokie** — wspólny serwer z produkcją | limity: 3/IP/dobę, 200 aktywnych, 2 MB plik, 20 MB na kopię; osobna baza demo; alert, gdy dysk demo > 80 % |
| **E** gość → admin / produkcja | **krytyczne** | flaga tylko na demo (fail-fast na produkcji); demo ma osobną bazę i sekrety; wysyłki zewnętrzne wyłączone dla spółek gościnnych |

Nowe ryzyka do `RYZYKA.md`: obciążenie wspólnego serwera przez demo (D); wymaga osobnego limitu zasobów
kontenera demo w Coolify. Bez zgody PO na limity zasobów — nie wdrażamy.

## Konsekwencje

- Dużo kodu: założenie i usuwanie kopii, limity, wyłączenie wysyłek per spółka, testy izolacji per trasa.
  Szacunek: 3–5 dni pracy w 2–3 PR-ach.
- Wspólne demo tylko do odczytu zostaje (wejście bez czekania).
- Test izolacji per trasa wzmacnia też produkcję (każda nowa trasa musi przejść test „spółka A ≠ B”).

## Pytania do PO (bez odpowiedzi — nie zaczynamy kodu)

1. Czy limity są akceptowalne: 24 h życia kopii, 3 kopie na IP na dobę, 200 aktywnych naraz?
2. Czy demo może dostać osobny limit pamięci/CPU w Coolify (żeby nie spowalniało produkcji)?
3. Czy kopia ma pozwalać na wgrywanie plików (PDF dokumentów), czy wystarczą pliki pokazowe?
