# Zrzuty i GIF

Wszystkie na danych pokazowych (`python -m scripts.seed_demo --wyczysc-wszystko`, patrz README),
nigdy na danych firmowych. Zrzuty PNG: 1440×860, konto `demo`, lokalna instancja ze świeżym seedem.

| Plik | Co pokazuje | Status |
|---|---|---|
| `demo.gif` | 16 s: karta kontenera → Edytuj → błędna cyfra kontrolna ISO 6346 → komunikat → poprawka → zakładka Historia (było → jest) | gotowe |
| `powitanie-demo.png` | ekran powitalny konta demo (4 kroki) nad kolejką | gotowe |
| `kolejka.png` | ekran 6 z [03-user-flow.md](../03-user-flow.md): kolejka bieżącego tygodnia pogrupowana dniami awizacji | gotowe |
| `karta-kontenera.png` | ekran 8: karta kontenera, etap procesu, zakładka Historia | gotowe |
| `automatyzacje.png` | ekran Automatyzacje: 26 automatów, stan, przebiegi, efekty, zaoszczędzony czas | gotowe — `PW_SHOT` w `e2e/demo/recruiter.spec.ts` |
| `symuluj-dzien.png` | „Symuluj dzień”: 5 kroków obiegu automatów na danych demo | gotowe — jw. |
| `odczyt-faktur-ai.png` | odczyt faktur: reguły / ML / człowiek tydzień po tygodniu i trafność wg pewności | gotowe — jw. |
| `przebieg-procesu.png` | przebieg procesu: czas w etapach (mediana, p90) i kontenery dłużej niż zwykle | gotowe — jw. |
| `sledzenie.png` | mapa śledzenia: kontenery w portach załadunku, przeładunku i docelowych | gotowe |
| `awizacja-link.png` | ekran 12: formularz awizacji otwarty z linku, bez logowania | `<DO UZUPEŁNIENIA>` |


Odświeżenie zrzutów ekranu Automatyzacje (komputer 1440×900):

```bash
cd frontend
PW_SHOT=/tmp/shot npx playwright test -c playwright.demo.config.ts -g Automatyzacje --project=desktop
# → /tmp/shot-desktop-{automatyzacje,symulacja,odczyt-ai,przebieg}.png
```
