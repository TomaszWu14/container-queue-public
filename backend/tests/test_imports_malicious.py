"""US-006 (R-07, SR-006): spreparowane pliki nie zatrzymują aplikacji — XML z DTD/encjami („billion
laughs”, XXE) odrzucony z 422, ZIP-bomba (silna kompresja, zaniżony rozmiar w nagłówku) pominięta
z powodem albo odrzucona 413, a proces obsługuje kolejne żądania."""
import io
import zipfile

from app.invoices import sad_parse
from tests.test_archive_upload import _post, _zip
from tests.test_invoice_conformity import _container
from tests.test_invoices_checks import _pdf, _setup

BILLION_LAUGHS = (b'<?xml version="1.0"?><!DOCTYPE SADUE [<!ENTITY a "aaaaaaaaaa">'
                  + b"".join(f'<!ENTITY a{i} "{"&a;" * 10}">'.encode() for i in range(1, 9))
                  + b']><SADUE P22WalutaSADu="&a8;"/>')
XXE = (b'<?xml version="1.0"?><!DOCTYPE SADUE [<!ENTITY x SYSTEM "file:///etc/passwd">]>'
       b'<SADUE P22WalutaSADu="&x;"/>')


def test_xml_bombs_rejected_before_parsing():
    assert sad_parse.parse_xml(BILLION_LAUGHS) is None
    assert sad_parse.parse_xml(XXE) is None


def _bomb_zip(size_mb: int = 5) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("4500/lista.csv", b"0" * (size_mb * 1024 * 1024))   # ~1000× kompresji
        archive.writestr("4500/ci.pdf", _pdf(1))
    return buf.getvalue()


def test_high_ratio_entry_skipped_rest_of_archive_kept(client, admin_headers, db_session,
                                                       monkeypatch, tmp_path):
    company, sup = _setup(db_session, monkeypatch, tmp_path)
    cid = _container(client, admin_headers, company, sup)
    resp = _post(client, admin_headers, cid, _bomb_zip())
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["pdfs"] == 1
    assert "lista.csv (podejrzanie silna kompresja — możliwa zip-bomba)" in body["skipped"]


def test_lying_header_cannot_inflate_past_declared_size(client, admin_headers, db_session,
                                                        monkeypatch, tmp_path):
    """Nagłówek deklaruje mały plik, dane rozpakowują się do dużo większego: zipfile czyta najwyżej
    zadeklarowaną liczbę bajtów, a niezgodna suma kontrolna kończy się pominięciem pliku."""
    company, sup = _setup(db_session, monkeypatch, tmp_path)
    cid = _container(client, admin_headers, company, sup)
    data = bytearray(_bomb_zip(size_mb=2))
    real = (2 * 1024 * 1024).to_bytes(4, "little")
    fake = (1000).to_bytes(4, "little")
    assert data.count(real) == 2                     # nagłówek lokalny + katalog centralny
    data = bytes(data).replace(real, fake)
    resp = _post(client, admin_headers, cid, data)
    assert resp.status_code == 201, resp.text
    assert any(s.startswith("lista.csv") for s in resp.json()["skipped"])
    assert client.get("/api/health").status_code == 200   # proces żyje


def test_total_uncompressed_limit_413(client, admin_headers, db_session, monkeypatch, tmp_path):
    company, sup = _setup(db_session, monkeypatch, tmp_path)
    cid = _container(client, admin_headers, company, sup)
    monkeypatch.setattr("app.routers.archive_upload.MAX_UNCOMPRESSED_MB", 1)
    assert _post(client, admin_headers, cid, _bomb_zip()).status_code == 413


def test_ordinary_documents_not_flagged(client, admin_headers, db_session, monkeypatch, tmp_path):
    company, sup = _setup(db_session, monkeypatch, tmp_path)
    cid = _container(client, admin_headers, company, sup)
    resp = _post(client, admin_headers, cid, _zip({"4500/ci.pdf": _pdf(2), "4500/pl.pdf": _pdf(3)}))
    assert resp.status_code == 201 and resp.json()["skipped"] == []
