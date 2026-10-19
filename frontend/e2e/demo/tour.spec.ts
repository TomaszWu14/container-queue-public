import { expect, test, type Page } from '@playwright/test'

// Przewodnik po demo (US-081) od początku do końca — test i jednocześnie film do README (US-083):
// `sh scripts/record_demo_video.sh przewodnik` nagrywa go w zwolnionym tempie; karta przewodnika
// na ekranie służy za napisy (PL i EN). Bez PW_SLOWMO przechodzi szybko jak zwykły test.
// 7 ekranów z doładowaniem danych (telefon wolniejszy), a nagranie filmu z przerwami — dłuższy limit
test.setTimeout(process.env.PW_SLOWMO ? 300_000 : 90_000)

const linger = (page: Page, ms = 6500) => page.waitForTimeout(process.env.PW_SLOWMO && !process.env.PW_FRAMES ? ms : 0)

async function runTour(page: Page, labels: { start: string; next: string; done: string; step: RegExp }) {
  await page.goto('/demo')
  await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })
  await page.keyboard.press('Escape')
  await page.getByTestId('demo-banner').getByRole('button', { name: labels.start, exact: true }).click()
  const card = page.locator('.tour-card')
  for (let i = 0; i < 20; i++) {
    await expect(card).toBeVisible()
    await expect(card.getByText(labels.step)).toBeVisible()
    await expect(page.locator('.tour-highlight')).toHaveCount(1, { timeout: 15_000 })
    // film do README (US-083): klatka na krok, ffmpeg skleja je w pokaz (scripts/record_demo_video.sh)
    if (process.env.PW_FRAMES) {
      await page.waitForTimeout(1500)   // dane i przewinięcie do celu
      await page.screenshot({ path: `${process.env.PW_FRAMES}/step-${String(i + 1).padStart(2, '0')}.png` })
    }
    await linger(page)
    const done = card.getByRole('button', { name: labels.done })
    if (await done.count()) { await done.click(); break }
    await card.getByRole('button', { name: labels.next }).click()
  }
  await expect(card).toHaveCount(0)
}

test('przewodnik po demo: wszystkie kroki od kolejki do „Jak to zbudowano”', async ({ page }) => {
  await runTour(page, { start: 'Przewodnik', next: 'Dalej', done: 'Gotowe', step: /Krok \d+ z \d+/ })
})

test.describe('tour in English', () => {
  test.use({ locale: 'en-US' })
  test('demo tour: every step from the queue to “How it was built”', async ({ page }) => {
    await runTour(page, { start: 'Guided tour', next: 'Next', done: 'Done', step: /Step \d+ of \d+/ })
  })
})
