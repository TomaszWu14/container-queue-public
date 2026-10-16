"""US-004 (R-03, SR-007): czy zawartość pliku zgadza się z rozszerzeniem — nie ufamy nazwie ani
Content-Type od przeglądarki. Plik `x.pdf`, który nie jest PDF-em, nie trafia do kontenera i nie
krąży między firmami pod fałszywą nazwą.

Sprawdzamy typy z pewną sygnaturą: PDF, obrazy, DOCX/XLSX (ZIP z `[Content_Types].xml`), ZIP i tekst
(bez bajtów NUL; UTF-16 z BOM-em dozwolony — tak zapisuje CSV Excel). Bez sprawdzenia zostają
`UNVERIFIED`: stary .doc/.xls (eksporty „.xls” z systemów bywają HTML-em lub CSV), .msg i .eml —
odrzucanie łamałoby realny obieg; ryzyko w `docs/bezpieczenstwo/RYZYKA.md` (R-03)."""
import io
import zipfile

IMAGE_EXTS = frozenset({"png", "jpg", "jpeg", "webp", "gif"})
TEXT_EXTS = frozenset({"txt", "csv", "xml", "json"})
OOXML_EXTS = frozenset({"docx", "xlsx"})
UNVERIFIED = frozenset({"doc", "xls", "eml", "msg"})

_TEXT_PROBE = 8192


def looks_like_image(head: bytes) -> bool:
    """Obraz po sygnaturze bajtowej (JPEG, PNG, GIF, WEBP, HEIC/HEIF)."""
    if head.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a")):
        return True
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return True
    return head[4:8] == b"ftyp"   # HEIC/HEIF (kontener ISO-BMFF)


def _is_text(content: bytes) -> bool:
    head = content[:_TEXT_PROBE]
    return head.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" not in head


def _is_ooxml(content: bytes) -> bool:
    if not content.startswith(b"PK\x03\x04"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            return "[Content_Types].xml" in archive.namelist()   # tylko katalog, bez rozpakowania
    except (zipfile.BadZipFile, OSError, ValueError):
        return False


def content_matches(extension: str, content: bytes) -> bool:
    """True, gdy zawartość pasuje do rozszerzenia (albo typ jest w `UNVERIFIED`)."""
    ext = extension.lower().lstrip(".")
    if ext == "pdf":
        return b"%PDF-" in content[:1024]   # nagłówek może być poprzedzony śmieciami (do 1 KB)
    if ext in IMAGE_EXTS:
        return looks_like_image(content[:16])
    if ext in OOXML_EXTS:
        return _is_ooxml(content)
    if ext == "zip":
        return content[:4] in (b"PK\x03\x04", b"PK\x05\x06")
    if ext in TEXT_EXTS:
        return _is_text(content)
    return True


def mismatch_message(extension: str) -> str:
    ext = extension.lower().lstrip(".") or "?"
    return (f"Plik nie jest prawdziwym plikiem .{ext} — zawartość nie zgadza się z rozszerzeniem. "
            "Zapisz go ponownie we właściwym formacie.")
