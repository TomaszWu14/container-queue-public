/* global process, console */
// Progi Lighthouse dla strony logowania (druga lista PO, pkt 14). Użycie:
//   node scripts/lighthouse-assert.mjs raport.json [plik-podsumowania.md]
// Czyta raport JSON z `lighthouse --output=json`, wypisuje wyniki, dopisuje tabelę do podsumowania
// (GitHub: $GITHUB_STEP_SUMMARY) i kończy kodem 1, gdy którakolwiek kategoria jest poniżej progu.
import { appendFileSync, readFileSync } from 'node:fs'

const THRESHOLDS = { performance: 0.7, accessibility: 0.95, 'best-practices': 0.95, seo: 0.9 }

const [, , reportPath, summaryPath] = process.argv
const report = JSON.parse(readFileSync(reportPath, 'utf-8'))
const rows = Object.entries(THRESHOLDS).map(([id, min]) => {
  const score = report.categories[id]?.score ?? 0
  return { id, score: Math.round(score * 100), min: Math.round(min * 100), ok: score >= min }
})
const table = ['| Kategoria | Wynik | Próg |', '|---|---|---|',
  ...rows.map(r => `| ${r.id} | ${r.ok ? '✅' : '❌'} ${r.score} | ${r.min} |`)].join('\n')
console.log(table)
if (summaryPath) appendFileSync(summaryPath, `### Lighthouse — strona logowania\n\n${table}\n`)
const failed = rows.filter(r => !r.ok)
if (failed.length) {
  console.error(`Poniżej progu: ${failed.map(r => r.id).join(', ')}`)
  process.exit(1)
}
