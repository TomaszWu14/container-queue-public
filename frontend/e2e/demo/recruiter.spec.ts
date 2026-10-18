import { expect, test, type Page } from '@playwright/test'

// Ścieżka rekrutera: /demo wpuszcza bez hasła, ekran powitalny prowadzi przez „historię jednego
// kontenera”, pulpit pokazuje wartość i ryzyka, „Jak to zbudowano” — architekturę i decyzje.
// Na telefonie strona nie może przewijać się w bok.

// nagranie filmu (scripts/record_demo_video.sh, PW_SLOWMO): chwila na obejrzenie ekranu; w testach 0
const linger = (page: Page) => page.waitForTimeout(process.env.PW_SLOWMO ? 2500 : 0)

async function noSideScroll(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
  expect(overflow, 'strona przewija się w bok').toBeLessThanOrEqual(1)
}

async function namedButtons(page: Page) {
  // dostępność: każdy widoczny przycisk ma nazwę dla czytnika ekranu
  const nameless = await page.locator('button:visible').evaluateAll(buttons => buttons
    .filter(b => !(b.textContent ?? '').trim() && !b.getAttribute('aria-label') && !b.getAttribute('title'))
    .map(b => b.outerHTML.slice(0, 80)))
  expect(nameless, 'przyciski bez nazwy').toEqual([])
}

test('rekruter: od wejścia do historii kontenera, pulpitu i „Jak to zbudowano”', async ({ page }) => {
  await page.goto('/demo')
  await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })

  const story = page.getByText('Historia jednego kontenera (1 min)')
  await expect(story).toBeVisible()
  await linger(page)
  await namedButtons(page)
  await story.locator('xpath=ancestor::li').getByRole('button').click()

  await expect(page).toHaveURL(/\/kontenery\/\d+\?akcja=history/)
  const timeline = page.getByRole('list', { name: 'Przebieg' })
  await expect(timeline).toBeVisible()
  await expect(timeline.getByText(/Zlecono odprawę agencji/)).toBeVisible()
  await expect(timeline.getByText('Spedycja potwierdziła termin')).toBeVisible()
  await linger(page)
  await noSideScroll(page)

  await page.goto('/pulpit')
  await expect(page.getByRole('region', { name: 'Ile to oszczędza' })).toBeVisible()
  await expect(page.getByText(/zmian w aplikacji × \d+ min \(założenie\)/)).toBeVisible()
  await expect(page.getByRole('region', { name: 'Przepływ kontenerów przez proces' })).toBeVisible()
  await expect(page.getByRole('img', { name: /^Porty: / })).toBeVisible()
  if (process.env.PW_SHOT) await page.screenshot({ path: `${process.env.PW_SHOT}-${test.info().project.name}.png`, fullPage: true })
  await linger(page)
  await noSideScroll(page)
  await namedButtons(page)

  await page.goto('/jak-zbudowano')
  await expect(page.getByRole('heading', { name: 'Kluczowe decyzje' })).toBeVisible()
  await linger(page)
  await noSideScroll(page)
})

test('demo jest tylko do odczytu: zapis odcięty, ukryte widoki niedostępne', async ({ page }) => {
  await page.goto('/demo')
  await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })
  await page.keyboard.press('Escape')
  const status = await page.evaluate(async () =>
    (await fetch('/api/changes/feed', { credentials: 'include' })).status)
  expect(status).toBe(403)
  await page.goto('/dziennik-zmian')
  await expect(page.getByText(/Brak dostępu|Forbidden|403/i).first()).toBeVisible()
})

test('brama: numer z karty rozładunku → karta auta z przyciskiem wpuszczenia', async ({ page }) => {
  await page.goto('/demo')
  await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })
  await page.keyboard.press('Escape')
  await page.goto('/brama')
  const first = page.locator('.gate-row .gate-no').first()
  await expect(first).toBeVisible()
  await page.getByLabel('Numer kontenera').fill((await first.textContent()) ?? '')
  await page.getByRole('button', { name: 'Szukaj' }).click()
  await expect(page.locator('.gate-scan-found')).toBeVisible()
  await noSideScroll(page)
  if (process.env.PW_SHOT) await page.screenshot({ path: `${process.env.PW_SHOT}-brama-${test.info().project.name}.png` })
})

test('ekran Automatyzacje w demo: katalog, oszczędność, panele z danymi i „Symuluj dzień”', async ({ page }) => {
  await page.goto('/demo')
  await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })
  await page.keyboard.press('Escape')
  await page.goto('/automatyzacje')
  await expect(page.locator('.auto-table tbody tr').first()).toBeVisible()
  expect(await page.locator('.auto-table tbody tr').count()).toBeGreaterThan(20)
  await expect(page.locator('.auto-table tbody tr[data-status="error"]')).toHaveCount(0)
  await expect(page.getByText(/Zaoszczędzony czas · 7 dni/)).toBeVisible()
  // seed demo: reguły, faktury dla panelu AI, historia statusów dla przebiegu procesu (żaden panel nie jest pusty)
  await expect(page.getByRole('region', { name: 'Reguły bez kodu' })).toBeVisible()
  await expect(page.getByRole('region', { name: 'Odczyt faktur: automat i człowiek' })
    .getByText('Brak faktur w tym okresie.')).toHaveCount(0)
  await expect(page.getByRole('region', { name: 'Przebieg procesu: gdzie kontenery stoją najdłużej' })
    .locator('.proc-table').first()).toBeVisible()
  const sim = page.getByRole('region', { name: 'Symuluj dzień' })
  await sim.getByRole('button', { name: 'Uruchom symulację' }).click()
  await expect(sim.locator('.sim-step')).toHaveCount(5)
  await expect(sim.getByText(/odczytał z treści numer/)).toBeVisible()
  if (process.env.PW_SHOT) {
    // zrzuty do README: kroki symulacji pojawiają się z animacją — czekamy na ostatni
    await expect(sim.locator('.sim-step').last()).toHaveCSS('opacity', '1')
    const shot = `${process.env.PW_SHOT}-${test.info().project.name}`
    await page.addStyleTag({ content: '[data-testid="demo-banner"]{display:none!important}.topnav{position:static!important}' })   // baner zasłania panele
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.screenshot({ path: `${shot}-automatyzacje.png` })
    await sim.screenshot({ path: `${shot}-symulacja.png` })
    await page.getByRole('region', { name: 'Odczyt faktur: automat i człowiek' }).screenshot({ path: `${shot}-odczyt-ai.png` })
    await page.getByRole('region', { name: 'Przebieg procesu: gdzie kontenery stoją najdłużej' })
      .screenshot({ path: `${shot}-przebieg.png` })
  }
  await linger(page)
  await noSideScroll(page)
  await namedButtons(page)
})

test.describe('gość z zagranicy', () => {
  test.use({ locale: 'en-US' })
  test('przeglądarka po angielsku → demo od razu po angielsku', async ({ page }) => {
    await page.goto('/demo')
    await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })
    await page.keyboard.press('Escape')
    await page.goto('/automatyzacje')
    await expect(page.getByRole('region', { name: 'Simulate a day' })).toBeVisible()
  })
})
