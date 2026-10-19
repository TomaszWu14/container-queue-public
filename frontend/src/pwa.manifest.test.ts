// US-078: aplikacja „na ekran telefonu” (PWA) — manifest kompletny dla instalacji w Chrome/Edge/Android
// (nazwa, start, tryb standalone, ikony PNG 192 i 512 + maskable) i podpięty w index.html razem z ikoną dla iOS.
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const root = resolve(__dirname, '..')
const manifest = JSON.parse(readFileSync(resolve(root, 'public/manifest.json'), 'utf8'))
const html = readFileSync(resolve(root, 'index.html'), 'utf8')

describe('PWA', () => {
  it('manifest ma pola wymagane do instalacji', () => {
    expect(manifest.name).toBeTruthy()
    expect(manifest.short_name.length).toBeLessThanOrEqual(12)
    expect(manifest.start_url).toBe('/')
    expect(manifest.display).toBe('standalone')
    const sizes = manifest.icons.filter((i: { type: string }) => i.type === 'image/png').map((i: { sizes: string }) => i.sizes)
    expect(sizes).toEqual(expect.arrayContaining(['192x192', '512x512']))
    expect(manifest.icons.some((i: { purpose?: string }) => i.purpose === 'maskable')).toBe(true)
  })

  it('wszystkie ikony i skróty wskazują istniejące pliki', () => {
    const srcs = [...manifest.icons, ...manifest.shortcuts.flatMap((s: { icons: unknown[] }) => s.icons)]
      .map((i: { src: string }) => i.src)
    for (const src of srcs) expect(existsSync(resolve(root, 'public', src.slice(1))), src).toBe(true)
  })

  it('index.html linkuje manifest, kolor paska i ikonę iOS', () => {
    expect(html).toContain('rel="manifest" href="/manifest.json"')
    expect(html).toContain('name="theme-color"')
    expect(html).toContain('rel="apple-touch-icon"')
    expect(existsSync(resolve(root, 'public/icons/apple-touch-icon.png'))).toBe(true)
  })
})
