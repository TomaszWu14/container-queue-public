# Container queue — planning import deliveries

*[Polska wersja](README.md)*

**One shared view of container deliveries for the logistics teams of several companies, their warehouses,
freight forwarders and the customs agency — replacing an Excel sheet sent around by email.**

![An invalid container number stopped by ISO 6346 validation, the fix and the change history entry](docs/screenshots/demo.gif)

📹 [Walkthrough — 2 min, captions, no sound](docs/video/prezentacja.mp4) ·
🎬 [Recruiter path — 20 s](docs/video/sciezka-rekrutera.mp4)

🌐 **Live demo, no sign-up: [container.queue.twapp.pl/demo](https://container.queue.twapp.pl/demo)** — read-only
account with 150 fictional containers. The app opens in English for browsers outside Poland and Portugal (language switch in the sidebar or on the login screen).
Try the **Automations** screen and press **“Simulate a day”**.

<table>
  <tr>
    <td><img src="docs/screenshots/automatyzacje.png" alt="Automations screen: catalog with status, runs, effects and time saved"></td>
    <td><img src="docs/screenshots/symuluj-dzien.png" alt="Simulate a day: email, container number, invoice, rules, n8n event and minutes saved"></td>
  </tr>
  <tr>
    <td align="center">Automations: what runs on its own, whether it works, time saved</td>
    <td align="center">“Simulate a day”: the automation flow step by step on demo data</td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/odczyt-faktur-ai.png" alt="Invoice reading: rules, ML model and people, and model accuracy by confidence"></td>
    <td><img src="docs/screenshots/przebieg-procesu.png" alt="Process flow: time per stage and containers stuck longer than usual"></td>
  </tr>
  <tr>
    <td align="center">AI invoice reading: who matched the lines, how accurate the model is</td>
    <td align="center">Process mining from the status history</td>
  </tr>
</table>

*Screenshots show the Polish UI; the app switches to English for English-language browsers.*

> **Portfolio project.** Company names are fictional, demo and test data are synthetic.
> The code is shared for review, all rights reserved — [`LICENSE`](LICENSE).

## Problem → solution

The delivery queue of several companies — about **200 containers a month**, 4 companies, 2 warehouses,
3 forwarders — lived in one Excel sheet. Keeping it up to date, reconciling versions and answering emails
took **4 logistics people about 30 hours a week**. The sheet had no container status, no change history
and no validation; partners worked on copies.

The app gives every party the same container state — from the purchase order, through the vessel and
customs clearance, to unloading — with a history of every change and data separated per company and partner.

## Automation — what the app does on its own

| Area | Examples | Human role |
|---|---|---|
| Documents | email → document inbox (container number read from the text), invoice reading (OCR + rules + ML model with a confidence threshold), customs draft from email | confirms with one click; decides on uncertain suggestions |
| Deadlines | demurrage warning, missing documents before ETA, warehouse overload forecast, vessel delays (AIS), port congestion | decides and acts |
| No-code rules | admin defines “when condition → notify” with a live preview | sets the rules |
| Communication | SMS to the driver the day before, morning digest per company, weekly purchasing digest | — |
| Integrations | HMAC-signed events to n8n / Power Automate / Make, SharePoint sync, Teams cards | builds the next steps |
| Data hygiene | GDPR purge of driver data after 30 days, log retention, backup restore test | reviews reports |

The **Automations** screen shows every automation with its trigger, action, live status (ok / late / failed /
off), runs and effects in the last 7 days, and **hours saved** — with the minutes-per-effect assumption shown
next to the result. It also shows invoice reading quality (share matched automatically, model accuracy by
confidence) and process flow analysis (median and 90th percentile time per stage, containers stuck longer
than usual).

Full matrix (what is automated, what stays with a person, and why):
[`docs/dla-rekrutera/MACIERZ-AUTOMATYZACJI.md`](docs/dla-rekrutera/MACIERZ-AUTOMATYZACJI.md) (Polish).

## Documents for reviewers (Polish)

| Document | What it covers |
|---|---|
| [Case study](docs/dla-rekrutera/STUDIUM-PRZYPADKU.md) | problem, approach, solution, how results are measured |
| [Document flow before / after](docs/dla-rekrutera/OBIEG-DOKUMENTU-PRZED-PO.md) | Mermaid diagrams of the email → document → delivery flow |
| [Metrics before / after](docs/dla-rekrutera/MIERNIKI-PRZED-PO.md) | baseline facts, where the app measures each metric, explicit assumptions |
| [Process](docs/02-proces.md) · [BPMN model](docs/bpmn/timporye-proces.bpmn) | whole process before and after, 5 lanes |
| [Requirements](docs/05-wymagania.md) · [Decisions](docs/06-decyzje.md) | 28 requirements with tests, 12 decisions with options considered |
| [Backlog](docs/analiza/HISTORYJKI.md) · [Assumptions](docs/analiza/ZALOZENIA.md) | user stories with acceptance criteria, assumptions awaiting the product owner |
| [Excel, Power BI, Power Automate](docs/MICROSOFT-365.md) · [n8n in 15 min](docs/WLASNA-AUTOMATYZACJA-15-MIN.md) | Power Query on the queue export, DAX measures, two flows; importable n8n workflow |
| [Threat model](docs/bezpieczenstwo/THREAT_MODEL.md) · [Risks](docs/bezpieczenstwo/RYZYKA.md) | STRIDE, risk register, GDPR |

## How the work is run

The repository is run like a three-person team — business analyst **[BA]**, developer **[DEV]**, security
**[SEC]** — with a product owner who decides scope, priorities and risks. Every change goes through analysis,
a STRIDE review, implementation with a test per acceptance criterion, security review and BA acceptance
([`CONTRIBUTING.md`](CONTRIBUTING.md)).

## Stack

FastAPI (Python) · SQLAlchemy + Alembic · PostgreSQL · React + TypeScript (Vite) · pytest, vitest, Playwright ·
Docker + Coolify · n8n. CI: 3000+ tests, backend coverage ≥ 92% enforced, Semgrep, Trivy, Bandit, secret scan,
role × route permission matrix checked by a test.

## Run locally

```bash
cp .env.example .env    # fill in POSTGRES_PASSWORD, SECRET_KEY, ADMIN_PASSWORD
docker compose up --build
# UI: http://localhost:8080   API: http://localhost:8000/docs
```

Demo data (wipes the target database): see [Jak uruchomić](README.md#jak-uruchomić).

## Contact

Built solo, July–October 2026: interviews and requirements, process and data model, decisions,
implementation, tests and deployment. Questions: tomasz.wierzbowski@op.pl
