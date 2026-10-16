"""US-013 (R-10): kopia poza serwer — po udanej kopii zaszyfrowane pliki idą do magazynu S3;
jawna kopia nigdy nie wychodzi z serwera; klucze nie trafiają do argumentów procesu; heartbeat
dopiero po udanej wysyłce."""
from tests.test_backup_scripts import _run_backup

AGE = "cat"   # „szyfrowanie” w teście: age -r KLUCZ czyta stdin, pisze stdout
SECRET = "sekret-testowy-123"  # gitleaks:allow — fałszywy klucz testowy


def _curl(log, exit_code=0):
    # zapisuje argumenty i konfigurację ze stdin (-K -); ping monitora też idzie przez curl
    return (f'echo "ARGS $*" >> {log}\n'
            f'case "$*" in *"-K -"*) sed "s/^/CONF /" >> {log} ;; esac\n'
            f'case "$*" in *aws-sigv4*) exit {exit_code} ;; esac\nexit 0')


def _env(**extra):
    return {"BACKUP_AGE_RECIPIENT": "age1test", "BACKUP_OFFSITE_URL": "https://s3.example.com/kopie/",
            "BACKUP_OFFSITE_REGION": "eu-central-003", "BACKUP_OFFSITE_ACCESS_KEY": "KEYID",
            "BACKUP_OFFSITE_SECRET_KEY": SECRET, **extra}


def test_offsite_uploads_encrypted_files_without_secret_in_args(tmp_path):
    log = tmp_path / "curl.log"
    proc, out = _run_backup(tmp_path, "echo 'SELECT 1;'", bins={"age": AGE, "curl": _curl(log)},
                            **_env(BACKUP_PING_URL="https://ping.example/x"))
    assert proc.returncode == 0, proc.stderr
    files = sorted(p.name for p in out.iterdir())
    assert all(f.endswith(".age") for f in files) and len(files) == 2
    lines = log.read_text().splitlines()
    uploads = [line for line in lines if line.startswith("ARGS") and "aws-sigv4" in line]
    assert len(uploads) == 2
    for name in files:
        assert any(f"https://s3.example.com/kopie/{name}" in line for line in uploads), name
    assert all("aws:amz:eu-central-003:s3" in line for line in uploads)
    assert not any(SECRET in line for line in lines if line.startswith("ARGS"))   # nie w `ps`
    assert any(line == f'CONF user = "KEYID:{SECRET}"' for line in lines)
    # heartbeat po wysyłce (ostatnie wywołanie curl)
    assert "https://ping.example/x" in [line for line in lines if line.startswith("ARGS")][-1]


def test_offsite_refuses_plaintext_backup(tmp_path):
    log = tmp_path / "curl.log"
    proc, out = _run_backup(tmp_path, "echo 'SELECT 1;'", bins={"curl": _curl(log)},
                            **_env(BACKUP_AGE_RECIPIENT=""))
    assert proc.returncode != 0 and "BACKUP_AGE_RECIPIENT" in proc.stderr
    assert len(list(out.glob("timporye-*.sql.gz"))) == 1   # kopia lokalna powstała
    assert not log.exists() or "aws-sigv4" not in log.read_text()


def test_offsite_failure_is_loud_and_skips_heartbeat(tmp_path):
    log = tmp_path / "curl.log"
    proc, out = _run_backup(tmp_path, "echo 'SELECT 1;'", bins={"age": AGE, "curl": _curl(log, 22)},
                            **_env(BACKUP_PING_URL="https://ping.example/x"))
    assert proc.returncode != 0 and "poza serwer" in proc.stderr
    assert list(out.glob("timporye-*.sql.gz.age"))          # lokalna zostaje
    assert "ping.example" not in log.read_text()


def test_without_offsite_url_nothing_is_sent(tmp_path):
    log = tmp_path / "curl.log"
    proc, _ = _run_backup(tmp_path, "echo 'SELECT 1;'", bins={"age": AGE, "curl": _curl(log)},
                          BACKUP_AGE_RECIPIENT="age1test")
    assert proc.returncode == 0, proc.stderr
    assert not log.exists() or "aws-sigv4" not in log.read_text()
