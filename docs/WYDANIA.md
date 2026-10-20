# Wydania i wdrażanie demo

Demo (`docker-compose.demo.yml`) wdrażamy z **wydań**, nie z każdego scalenia do `main`. Przy kilkudziesięciu
scaleniach dziennie auto-deploy co chwilę przebudowywał demo w trakcie oglądania.

## Jednorazowo (Coolify + GitHub)

1. Coolify → zasób demo → **Configuration → General → Auto Deploy: wyłącz**.
2. Coolify → zasób demo → **Webhooks → Deploy Webhook**: skopiuj adres (`https://…/api/v1/deploy?uuid=…`).
   Coolify → **Keys & Tokens → API tokens**: nowy token z uprawnieniem *deploy*.
3. GitHub → repozytorium → **Settings → Secrets and variables → Actions**:
   `COOLIFY_DEPLOY_WEBHOOK` = adres z pkt 2 (tylko `https://`), `COOLIFY_TOKEN` = token.
   Bez tych sekretów workflow „Wydanie” tworzy samo wydanie, a demo wdrażasz ręcznie (Coolify → Redeploy).

## Każde wydanie

```sh
git checkout -b wydanie-0.2.0 origin/main
python scripts/przygotuj_wydanie.py 0.2.0     # [Unreleased] → [0.2.0], wersja w package.json i main.py
git commit -am "chore: wydanie 0.2.0" && git push -u origin wydanie-0.2.0   # PR → scalenie
git checkout main && git pull && git tag v0.2.0 && git push origin v0.2.0
```

Tag uruchamia workflow **„Wydanie”** (`.github/workflows/release.yml`):
1. sprawdza, że tag zgadza się z wersją w `frontend/package.json` i `backend/app/main.py` oraz że CHANGELOG ma sekcję wersji,
2. tworzy wydanie na GitHubie z notatkami z tej sekcji,
3. wywołuje deploy webhook Coolify (gdy są sekrety).

Numeracja [SemVer](https://semver.org/lang/pl/): nowe funkcje → `0.X.0`, same poprawki → `0.x.Y`.
