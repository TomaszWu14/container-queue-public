import { defineConfig, devices } from '@playwright/test'

// „Ścieżka rekrutera” (npm run e2e:demo): aplikacja na świeżej bazie z danymi demo (seed_demo), demo
// przeklikane jak przez rekrutera — na komputerze i na telefonie — z nagraniem wideo (test-results-demo/).
// Porty inne niż e2e (8000/5173), żeby oba zestawy mogły działać obok siebie.
const API_PORT = process.env.DEMO_API_PORT ?? '8011'
const WEB_PORT = process.env.DEMO_WEB_PORT ?? '5181'
const DEMO_ENV = {
  DATABASE_URL: 'sqlite:///./e2e-demo.db', RUN_BACKGROUND_JOBS: 'false', API_RATE_LIMIT_PER_MINUTE: '0', PUBLIC_RATE_LIMIT_PER_MINUTE: '0',
  REQUIRE_2FA_ADMIN: 'false', DEMO_READONLY_LOGINS: 'demo,demo-spedytor,demo-agencja,demo-magazyn',
  DEMO_PASSWORD: 'Demo-Portfolio-2026', UPLOADS_DIR: './e2e-demo-uploads',
}

export default defineConfig({
  testDir: './e2e/demo',
  fullyParallel: false,
  workers: 1,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never', outputFolder: 'playwright-report-demo' }]] : 'list',
  outputDir: 'test-results-demo',
  use: {
    locale: 'pl-PL',   // testy czytają polskie teksty; język startowy zależy od przeglądarki (detectLang)
    baseURL: `http://localhost:${WEB_PORT}`, video: 'on', trace: 'retain-on-failure',
    // PW_CHROMIUM: przeglądarka spoza Playwrighta (np. inna wersja w kontenerze); puste = wbudowana
    // PW_SLOWMO (ms): wolniejsze klikanie do nagrania filmu do README (scripts/record_demo_video.sh)
    launchOptions: {
      ...(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {}),
      slowMo: Number(process.env.PW_SLOWMO ?? 0),
    },
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } } },
    { name: 'telefon', use: { ...devices['Pixel 7'] } },
  ],
  webServer: [
    {
      command: `sh -c "rm -rf e2e-demo.db e2e-demo-uploads && python -m scripts.seed_demo --wyczysc-wszystko`
        + ` && python -m uvicorn app.main:app --port ${API_PORT}"`,
      cwd: '../backend',
      url: `http://localhost:${API_PORT}/api/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
      env: DEMO_ENV,
    },
    {
      command: `npm run dev -- --port ${WEB_PORT} --strictPort`,
      url: `http://localhost:${WEB_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: { VITE_API_TARGET: `http://localhost:${API_PORT}` },
    },
  ],
})
