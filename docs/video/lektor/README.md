# Film z lektorem (YouTube)

| Plik | Co to |
|---|---|
| `../prezentacja-lektor.mp4` | film 2:42, 1280×720, polski lektor, plansza tytułowa i końcowa z linkiem do demo |
| `../prezentacja-lektor.srt` | napisy PL do wgrania na YouTube osobno (w obrazie są już krótkie podpisy) |
| `../miniatura-youtube.png` | miniatura 1280×720 |
| `s01.mp3` … `s11.mp3` | kwestie lektora, po jednej na scenę |
| `plansze.html` | plansza tytułowa, końcowa i miniatura (`#intro`, `#outro`, `#thumb`) |

Obraz to `../prezentacja.mp4` (nagranie na danych pokazowych). Głos: ElevenLabs, model `eleven_v4`,
głos „Piotr Dokumentalny”. Odbudowa po zmianie kwestii, planszy albo nagrania:

```bash
python3 scripts/build_video_lektor.py
```

Skrypt przycina scenę z nagrania, a gdy kwestia jest dłuższa — zatrzymuje ostatnią klatkę, więc głos
nie rozjeżdża się z obrazem. Wycinki i teksty kwestii są w `SCENES` w skrypcie. Po zmianie tekstu
trzeba wygenerować nowe `sNN.mp3` i ewentualnie przesunąć wycinek.

## Scenariusz

| # | Obraz (sekundy w `prezentacja.mp4`) | Kwestia |
|---|---|---|
| 1 | 0–16 kolejka tygodnia | Kolejka dostaw kontenerów. Około dwustu kontenerów miesięcznie, cztery spółki, magazyny, spedytorzy i agencja celna. Dotąd wszystko żyło w jednym Excelu rozsyłanym mailem, bez historii zmian i bez walidacji. Cztery osoby w logistyce traciły na to około trzydziestu godzin tygodniowo. |
| 2 | 16–28 karta, błędny numer | Każdy kontener ma jedną kartę. Numer jest sprawdzany według normy ISO 6346. Literówka nie przejdzie, bo system liczy cyfrę kontrolną. |
| 3 | 28–38 historia zmian | Zamiast kolejnych wersji pliku jest jeden status. A każda zmiana trafia do historii: kto, kiedy, co było i co jest. |
| 4 | 38–46 mapa śledzenia | Śledzenie: statki z sygnału AIS, kontenery na trasie i w portach przeładunku. |
| 5 | 46–56 dokumenty, podział PDF | Odprawa celna. Faktura PDF od dostawcy trafia do kontenera. System dzieli plik na fakturę i packing listę, i sprawdza, czy to na pewno dokumenty tego kontenera. |
| 6 | 56–76 weryfikacja faktury, mail do agencji | Pozycje odczytane z PDF są dopasowane do kartoteki: polska nazwa, kod CN i wagi z packing listy. Do agencji celnej idzie gotowy mail z plikiem XML do WinSAD. Pozycje zgłoszenia są wyliczone prosto z faktury. |
| 7 | 76–96 awizacja, formularz spedytora | Awizacja. Logistyka wysyła spedytorowi prośbę o potwierdzenie terminu. Spedytor dostaje link w mailu i odpowiada bez zakładania konta i bez logowania. |
| 8 | 96–108 zatwierdzenie | Logistyka zatwierdza odpowiedź jednym kliknięciem. System rezerwuje termin i prosi o dane kierowców. To świadoma decyzja: spedytor nie musi mieć konta, więc małe spedycje nie wypadają z planowania. |
| 9 | 108–118 link jednorazowy | Link działa tylko raz i wygasa po kilku dniach. W bazie nie ma samego linku, jest tylko jego skrót SHA-256. |
| 10 | 118–128 dokumentacja: zakres | Świadomie poza zakresem: zapis do SAP, bo system tylko czyta jego eksporty, oraz tracking u armatora. To kolejny etap. |
| 11 | 128–134 repozytorium | Python, FastAPI, PostgreSQL i React. Kod i dokumentacja analityczna są na GitHubie, a wersję demo, bez logowania, otworzysz z linku w opisie. |

W tekście dla lektora liczby są zapisane słownie („ISO sześć-trzy-cztery-sześć”, „SHA dwieście
pięćdziesiąt sześć”), żeby syntezator ich nie przekręcił.

## Opis na YouTube (do wklejenia)

**Tytuł:** Kolejka dostaw kontenerów — z Excela do systemu (Python, FastAPI, React) | demo

**Opis:**

```text
Projekt portfolio: system planowania dostaw kontenerów importowych dla logistyki, magazynów,
spedytorów i agencji celnej — w miejsce Excela rozsyłanego mailem. Dane w filmie są fikcyjne.

▶ Demo bez logowania: https://container.queue.twapp.pl/demo
▶ Kod i dokumentacja analityczna: https://github.com/TomaszWu14/container-queue-public

0:00 Wstęp
0:04 Problem: Excel rozsyłany mailem
0:24 Karta kontenera i walidacja ISO 6346
0:36 Historia zmian i śledzenie statków (AIS)
0:54 Odprawa celna: PDF → XML do WinSAD
1:27 Awizacja bez konta spedytora
2:12 Zakres i technologia
2:35 Demo bez logowania

Python · FastAPI · PostgreSQL · React · TypeScript
```

**Tagi:** logistyka, kontenery, awizacja, odprawa celna, FastAPI, React, portfolio, analiza biznesowa

Przy wgrywaniu: miniatura `miniatura-youtube.png`, napisy `prezentacja-lektor.srt` (język: polski).
Rozdziały liczą się z długości scen w skrypcie — po przebudowie z innymi kwestiami sprawdź czasy.
