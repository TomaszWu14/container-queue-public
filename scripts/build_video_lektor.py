"""Film z lektorem na YouTube: docs/video/prezentacja.mp4 (obraz) + docs/video/lektor/sNN.mp3 (głos).

Każda scena to wycinek oryginalnego nagrania; gdy kwestia lektora jest dłuższa niż wycinek,
ostatnia klatka jest przytrzymywana (tpad), więc głos zawsze pasuje do obrazu. Na początku
i końcu plansze z docs/video/lektor/plansze.html (headless Chromium). Wynik:
  docs/video/prezentacja-lektor.mp4   — film 1280×720, AAC
  docs/video/prezentacja-lektor.srt   — napisy PL (osobny plik do YouTube)
  docs/video/miniatura-youtube.png    — miniatura 1280×720

Uruchomienie z katalogu repo (wymaga ffmpeg; plansze — Chromium z Playwright i
`npm ci` we frontend/ dla fontu IBM Plex):
  python3 scripts/build_video_lektor.py
Scenariusz i źródło głosu: docs/video/lektor/README.md.
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "docs" / "video"
LEKTOR = VIDEO / "lektor"
SRC = VIDEO / "prezentacja.mp4"

LEAD = 0.5   # cisza przed kwestią w scenie [s]
TAIL = 0.7   # oddech po kwestii [s]
INTRO = 4.0  # plansza tytułowa [s]
OUTRO = 7.0  # plansza końcowa [s]
FPS = 30

# (start, koniec) wycinka prezentacja.mp4 [s], plik głosu, tekst kwestii (= napisy .srt)
SCENES: list[tuple[float, float, str, str]] = [
    (0, 16, "s01", ("Kolejka dostaw kontenerów. Około dwustu kontenerów miesięcznie, cztery spółki, "
     "magazyny, spedytorzy i agencja celna. Dotąd wszystko żyło w jednym Excelu rozsyłanym mailem, "
     "bez historii zmian i bez walidacji. Cztery osoby w logistyce traciły na to około trzydziestu "
     "godzin tygodniowo.")),
    (16, 28, "s02", ("Każdy kontener ma jedną kartę. Numer jest sprawdzany według normy ISO 6346. "
     "Literówka nie przejdzie, bo system liczy cyfrę kontrolną.")),
    (28, 38, "s03", ("Zamiast kolejnych wersji pliku jest jeden status. A każda zmiana trafia do "
     "historii: kto, kiedy, co było i co jest.")),
    (38, 46, "s04", ("Śledzenie: statki z sygnału AIS, kontenery na trasie i w portach przeładunku.")),
    (46, 56, "s05", ("Odprawa celna. Faktura PDF od dostawcy trafia do kontenera. System dzieli plik "
     "na fakturę i packing listę, i sprawdza, czy to na pewno dokumenty tego kontenera.")),
    (56, 76, "s06", ("Pozycje odczytane z PDF są dopasowane do kartoteki: polska nazwa, kod CN i wagi "
     "z packing listy. Do agencji celnej idzie gotowy mail z plikiem XML do WinSAD. Pozycje "
     "zgłoszenia są wyliczone prosto z faktury.")),
    (76, 96, "s07", ("Awizacja. Logistyka wysyła spedytorowi prośbę o potwierdzenie terminu. Spedytor "
     "dostaje link w mailu i odpowiada bez zakładania konta i bez logowania.")),
    (96, 108, "s08", ("Logistyka zatwierdza odpowiedź jednym kliknięciem. System rezerwuje termin i "
     "prosi o dane kierowców. To świadoma decyzja: spedytor nie musi mieć konta, więc małe "
     "spedycje nie wypadają z planowania.")),
    (108, 118, "s09", ("Link działa tylko raz i wygasa po kilku dniach. W bazie nie ma samego linku, "
     "jest tylko jego skrót SHA-256.")),
    (118, 128, "s10", ("Świadomie poza zakresem: zapis do SAP, bo system tylko czyta jego eksporty, "
     "oraz tracking u armatora. To kolejny etap.")),
    (128, 133.8, "s11", ("Python, FastAPI, PostgreSQL i React. Kod i dokumentacja analityczna są na "
     "GitHubie, a wersję demo, bez logowania, otworzysz z linku w opisie.")),
]

ENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]


def run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def duration(path: Path) -> float:
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(path)))


def headless_chrome() -> str:
    found = sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell"))
    found += [p for p in (shutil.which("chromium"), shutil.which("google-chrome")) if p]
    if not found:
        sys.exit("brak Chromium do renderowania plansz (Playwright: /opt/pw-browsers)")
    return found[0]


def render_card(name: str, out: Path) -> None:
    url = (LEKTOR / "plansze.html").as_uri() + "#" + name
    run(headless_chrome(), "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
        "--window-size=1280,720", "--virtual-time-budget=2000", f"--screenshot={out}", url)


def card_clip(png: Path, secs: float, out: Path) -> None:
    fade = f"fade=in:st=0:d=0.6,fade=out:st={secs - 0.6}:d=0.6"
    run("ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(secs), "-i", str(png),
        "-f", "lavfi", "-t", str(secs), "-i", "anullsrc=r=48000:cl=stereo",
        "-vf", f"scale=1280:720,{fade}", "-shortest", *ENC, str(out))


def scene_clip(start: float, end: float, voice: Path, out: Path) -> float:
    """Wycinek + głos; zwraca długość sceny."""
    clip = end - start
    total = max(clip, LEAD + duration(voice) + TAIL)
    vf = f"fps={FPS},tpad=stop_mode=clone:stop_duration={total - clip + 0.1:.3f},trim=duration={total:.3f}"
    delay = int(LEAD * 1000)
    af = f"adelay={delay}|{delay},apad,atrim=duration={total:.3f},aresample=48000"
    run("ffmpeg", "-y", "-v", "error", "-ss", str(start), "-t", str(clip), "-i", str(SRC),
        "-i", str(voice), "-map", "0:v", "-map", "1:a", "-vf", vf, "-af", af,
        "-ac", "2", *ENC, str(out))
    return total


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def srt_cues(text: str, start: float, length: float) -> list[tuple[float, float, str]]:
    """Kwestia dzielona na zdania; czas proporcjonalny do liczby znaków."""
    parts = [p for p in re.split(r"(?<=[.:])\s+", text) if p]
    total = sum(len(p) for p in parts)
    cues, t = [], start
    for p in parts:
        d = length * len(p) / total
        cues.append((t, t + d, p))
        t += d
    return cues


def main() -> None:
    if not SRC.exists():
        sys.exit(f"brak {SRC}")
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        for name in ("intro", "outro", "thumb"):
            render_card(name, tmp / f"{name}.png")
        shutil.copy(tmp / "thumb.png", VIDEO / "miniatura-youtube.png")

        parts = [tmp / "00_intro.mp4"]
        card_clip(tmp / "intro.png", INTRO, parts[0])
        cues: list[tuple[float, float, str]] = []
        t = INTRO
        for i, (start, end, voice, text) in enumerate(SCENES, 1):
            out = tmp / f"{i:02d}.mp4"
            vpath = LEKTOR / f"{voice}.mp3"
            length = scene_clip(start, end, vpath, out)
            cues += srt_cues(text, t + LEAD, duration(vpath))
            parts.append(out)
            t += length
            print(f"{voice}: {length:5.1f} s (wycinek {end - start:4.1f} s)")
        parts.append(tmp / "99_outro.mp4")
        card_clip(tmp / "outro.png", OUTRO, parts[-1])

        listing = tmp / "parts.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in parts))
        out = VIDEO / "prezentacja-lektor.mp4"
        # loudnorm: głos ok. -16 LUFS (poziom zalecany dla YouTube)
        run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
            "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart", str(out))

    srt = "\n".join(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n"
                    for n, (a, b, txt) in enumerate(cues, 1))
    (VIDEO / "prezentacja-lektor.srt").write_text(srt, encoding="utf-8")
    print(f"gotowe: {out.relative_to(ROOT)} ({duration(out):.1f} s), napisy .srt, miniatura")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
