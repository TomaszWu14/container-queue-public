import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

// Dostępność stron po zalogowaniu (trzecia lista PO, pkt 11): axe-core (WCAG 2.1 A/AA) na kluczowych ekranach
// konta demo — kolejka, karta kontenera, pulpit, Automatyzacje. Lighthouse w CI mierzy tylko logowanie;
// tu pilnujemy ekranów, na których ludzie pracują. Błędy „serious”/„critical” = czerwony test.

test.use({ video: 'off' })   // nagranie zbędne — wynik to lista naruszeń

const PAGES = [
  { name: 'kolejka', path: '/kolejka' },
  { name: 'pulpit', path: '/pulpit' },
  { name: 'automatyzacje', path: '/automatyzacje' },
]

for (const p of PAGES) {
  test(`dostępność: ${p.name}`, async ({ page }) => {
    await page.goto('/demo')
    await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })
    await page.keyboard.press('Escape')
    await page.goto(p.path)
    await page.waitForLoadState('networkidle')
    const result = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze()
    const blocking = result.violations.filter(v => v.impact === 'serious' || v.impact === 'critical')
    const report = blocking.map(v => `${v.id} (${v.impact}): ${v.help} — ${v.nodes.length}× np. ${v.nodes[0]?.target.join(' ')}`)
    expect(report, `naruszenia WCAG na ${p.path}`).toEqual([])
  })
}

test('dostępność: karta kontenera', async ({ page }) => {
  await page.goto('/demo')
  await expect(page.getByTestId('demo-banner')).toBeVisible({ timeout: 30_000 })
  await page.keyboard.press('Escape')
  await page.goto('/kolejka')
  const cid = await page.locator('tr[data-cid]').first().getAttribute('data-cid')
  await page.goto(`/kontenery/${cid}`)
  await page.waitForLoadState('networkidle')
  const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze()
  const blocking = result.violations.filter(v => v.impact === 'serious' || v.impact === 'critical')
  expect(blocking.map(v => `${v.id}: ${v.nodes.length}× ${v.nodes[0]?.target.join(' ')}`), 'naruszenia WCAG na karcie').toEqual([])
})
