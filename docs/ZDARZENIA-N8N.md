# Zdarzenia z aplikacji do n8n / Power Automate / Make

US-035. Każde powiadomienie systemu (alert o karze za przestój, opóźniona odprawa, nowy plik, zmiana
statusu…) aplikacja wysyła też jako **zdarzenie HTTP** (webhook) na jeden adres. Tam dalsze kroki
składa się bez programowania: n8n, Power Automate albo Make. Przykład: „opóźniona odprawa” →
wiadomość na Teams kierownika i wiersz w Excelu na SharePoincie.

Wysyłka idzie w tle i nie blokuje pracy w aplikacji. Jeśli odbiorca nie działa, operacja w aplikacji
i tak się udaje, a wynik wysyłki (sukces albo błąd) trafia do dziennika zadań. Ekran
**Automatyzacje → „Zdarzenia do n8n”** pokazuje liczbę wysłanych zdarzeń i błędów z 7 dni.
Administrator ma tam przycisk **„Wyślij zdarzenie testowe”**. Nieudana wysyłka zapala dzwonek
administratora.

## Konfiguracja (Coolify → zmienne środowiskowe)

| Zmienna | Co robi |
|---|---|
| `AUTOMATION_WEBHOOK_URL` | Adres odbiorcy, np. `https://domena.pl/n8n/webhook/timporye`. Pusty = kanał wyłączony. |
| `AUTOMATION_WEBHOOK_SECRET` | Sekret do podpisu HMAC. **Ustaw go zawsze** — bez niego odbiorca nie odróżni zdarzenia od podróbki. |

Panel **Administracja → Integracje** pokazuje, czy kanał działa, czy podpis jest włączony i kiedy
wyszło ostatnie zdarzenie.

## Format zdarzenia (wersja 1)

`POST`, `Content-Type: application/json`, nagłówek `X-Timporye-Signature: sha256=<hex>`.

```json
{
  "id": "4f1c2a9e0b7d4c3e8a6f5d2b1c0e9a87",
  "version": 1,
  "source": "timporye",
  "event": "customs-delay",
  "title": "Odprawa MSCU1234565 trwa 4 dni",
  "body": "Zlecona 2026-10-13, agencja: Agencja Celna Demo",
  "sent_at": "2026-10-17T08:15:02.123456",
  "container_id": 1287,
  "recipients": 3
}
```

| Pole | Znaczenie |
|---|---|
| `id` | Unikalny identyfikator zdarzenia — **deduplikacja** po stronie odbiorcy (ponowienie nie zrobi dwa razy tego samego). |
| `version` | Wersja formatu; zmiana niezgodna wstecz = nowa wersja. |
| `event` | Rodzaj zdarzenia (tabela niżej) — po nim rozgałęzia się workflow. |
| `title`, `body` | Tekst powiadomienia (taki jak w dzwonku w aplikacji). |
| `sent_at` | Czas wysłania (UTC). |
| `container_id` | Kontener, którego dotyczy (albo `null`) — szczegóły pobiera się API z tokenem serwisowym (`docs/N8N.md`). |
| `recipients` | Ilu osobom aplikacja pokazała powiadomienie. |

Zdarzenie zawiera tylko to, co i tak widzą odbiorcy powiadomienia. Bez danych osobowych kierowców
i bez załączników.

### Najczęstsze rodzaje (`event`)

| `event` | Kiedy |
|---|---|
| `demurrage` | Zbliża się koniec wolnego czasu w porcie (kara za przestój). |
| `customs-delay` | Odprawa zlecona albo w rewizji dłużej niż próg dni. |
| `docs-missing` | Przed ETA brakuje wymaganych dokumentów. |
| `forecast-overload` | Prognoza: więcej rozładunków niż limit magazynu. |
| `eta_overdue`, `eta_drift` | Przekroczone ETA / statek spóźnia się według AIS. |
| `port_congestion` | Zator w porcie (statki na redzie > 2× mediana). |
| `customs`, `order`, `planned`, `file`, `avizo`, `driver` | Zmiany w odprawie, zamówieniu, planie, dokumentach, awizacji, danych kierowcy. |
| `complaint_draft`, `complaint_reminder`, `complaint_deadline` | Reklamacje: szkic z opóźnienia, brak odpowiedzi, termin. |
| `stale-import` | Dane z SAP starsze niż próg. |
| `backup_verify_failed`, `system-error` | Problemy techniczne (do kanału admina). |
| `test` | Zdarzenie testowe z ekranu Automatyzacje. |

## Sprawdzenie podpisu

Podpis to HMAC-SHA256 z **surowej treści żądania** i sekretu, w formacie `sha256=<hex>` (jak w
webhookach GitHuba). Podpis trzeba liczyć z bajtów, które przyszły, nie z ponownie
zserializowanego JSON-a.

**n8n** — węzeł *Webhook* z opcją *Raw Body*, potem węzeł *Code* (JavaScript):

```js
const crypto = require('crypto');
const raw = Buffer.from($input.first().binary.data.data, 'base64');
const expected = 'sha256=' + crypto.createHmac('sha256', $env.TIMPORYE_SECRET).update(raw).digest('hex');
const got = $input.first().json.headers['x-timporye-signature'] || '';
if (got.length !== expected.length || !crypto.timingSafeEqual(Buffer.from(got), Buffer.from(expected))) {
  throw new Error('Zły podpis — zdarzenie odrzucone');
}
return [{ json: JSON.parse(raw.toString('utf8')) }];
```

**Python** (np. Azure Function przed Power Automate):

```python
import hashlib, hmac

def valid(raw_body: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")
```

**Power Automate / Make.** Wyzwalacz „When an HTTP request is received” (Power Automate) i *Custom
webhook* (Make) przyjmą zdarzenie bez zmian. Same jednak nie sprawdzą HMAC. Są dwa wyjścia:
- **Bramka n8n:** n8n sprawdza podpis i przekazuje zdarzenie dalej. To rozwiązanie zalecane.
- **Tajny adres:** adres wyzwalacza Power Automate zawiera podpis SAS, ale wtedy kto zna adres,
  może wysłać zdarzenie.

## Ponowienia i błędy

- **Jedna próba na zdarzenie:** kod HTTP spoza 2xx albo błąd sieci to błąd w dzienniku zadań
  (`n8n_events`, rodzaj zdarzenia jako funkcja) i dzwonek administratora. Kolejne powiadomienia
  idą normalnie. Ponawianie zostaje po stronie odbiorcy, np. kolejka w n8n.
- **Kolejność nie jest gwarantowana:** do porządkowania służą `sent_at` i `id`.
