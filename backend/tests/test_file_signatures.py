"""US-004 (R-03, SR-007): wgrany plik sprawdzany po zawartości, nie tylko po rozszerzeniu.
Plik `x.pdf`, który nie jest PDF-em, jest odrzucany i nic nie zostaje zapisane; prawdziwe pliki
przechodzą jak dotąd; typy bez pewnej sygnatury (.msg, .eml, .doc, .xls) są przyjmowane."""
import io

import pytest

from app.file_signatures import content_matches
from app.models import Attachment
from tests.conftest import pdf_bytes, xlsx_bytes
from tests.test_archive_upload import _post, _zip
from tests.test_invoice_conformity import _container
from tests.test_invoices_checks import _pdf, _setup

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 16


@pytest.mark.parametrize("ext,content", [
    ("pdf", pdf_bytes("ok")), ("png", PNG), ("jpg", JPG), ("jpeg", PNG), ("gif", b"GIF89a" + b"\x00" * 8),
    ("webp", b"RIFF\x00\x00\x00\x00WEBPVP8 "), ("xlsx", xlsx_bytes("ok")), ("docx", xlsx_bytes("ok")),
    ("zip", _zip({"a.txt": b"a"})), ("csv", b"a;b\n1;2\n"), ("txt", "zażółć".encode()),
    ("csv", "a;b".encode("utf-16")), ("json", b'{"a": 1}'), ("xml", b"<a/>"),
    ("msg", b"\xd0\xcf\x11\xe0 cokolwiek"), ("eml", b"From: x"), ("xls", b"<html>"), ("doc", b"\x00\x01"),
])
def test_matching_content_accepted(ext, content):
    assert content_matches(ext, content)


@pytest.mark.parametrize("ext,content", [
    ("pdf", b"MZ\x90\x00 to jest program"), ("pdf", b""), ("png", b"%PDF-1.7"), ("jpg", b"<html>"),
    ("xlsx", b"x"), ("xlsx", _zip({"a.txt": b"a"})), ("docx", b"PK\x03\x04 uciety"),
    ("zip", b"MZ"), ("csv", b"a;b\x00\x01"), ("txt", b"MZ\x90\x00\x03\x00"),
])
def test_mismatched_content_rejected(ext, content):
    assert not content_matches(ext, content)


def _upload(client, headers, cid, name, content):
    return client.post(f"/api/containers/{cid}/attachments", headers=headers,
                       files={"file": (name, io.BytesIO(content), "application/pdf")})


def test_fake_pdf_rejected_and_nothing_saved(client, admin_headers, db_session, monkeypatch, tmp_path):
    company, sup = _setup(db_session, monkeypatch, tmp_path)
    cid = _container(client, admin_headers, company, sup)
    resp = _upload(client, admin_headers, cid, "faktura.pdf", b"MZ\x90\x00 program udajacy PDF")
    assert resp.status_code == 422 and "nie jest prawdziwym plikiem .pdf" in resp.json()["detail"]
    assert db_session.query(Attachment).filter_by(container_id=cid).count() == 0
    assert not any(p.is_file() for p in tmp_path.rglob(f"{cid}_*"))


def test_real_files_and_unverified_types_accepted(client, admin_headers, db_session, monkeypatch, tmp_path):
    company, sup = _setup(db_session, monkeypatch, tmp_path)
    cid = _container(client, admin_headers, company, sup)
    for name, content in (("kalk.xlsx", xlsx_bytes("k")), ("foto.png", PNG), ("lista.csv", b"a;b\n"),
                          ("mail.msg", b"\xd0\xcf\x11\xe0 outlook")):
        resp = _upload(client, admin_headers, cid, name, content)
        assert resp.status_code == 201, (name, resp.text)


def test_zip_entry_with_fake_content_skipped(client, admin_headers, db_session, monkeypatch, tmp_path):
    company, sup = _setup(db_session, monkeypatch, tmp_path)
    cid = _container(client, admin_headers, company, sup)
    data = _zip({"4500/ci.pdf": _pdf(2), "4500/kalk.xlsx": xlsx_bytes("ok"), "4500/oszust.xlsx": b"MZ"})
    resp = _post(client, admin_headers, cid, data)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["attachments"] == 1
    assert "oszust.xlsx (zawartość nie zgadza się z rozszerzeniem)" in body["skipped"]
