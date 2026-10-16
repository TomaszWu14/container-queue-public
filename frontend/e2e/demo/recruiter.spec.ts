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
