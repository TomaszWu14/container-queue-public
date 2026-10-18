// @vitest-environment jsdom
// US-036: kreator reguł bez kodu — admin dodaje regułę z listy warunków (etap tylko dla warunku
// „przed etapem”), podgląd pokazuje dzisiejsze kontenery, zapis wysyła całą listę; logistyka tylko czyta.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'

const { get, put } = vi.hoisted(() => ({ get: vi.fn(), put: vi.fn() }))
vi.mock('../api', () => ({ api: { get, put }, errorMessage: (e: unknown) => (e as Error).message }))

import AutomationRulesPanel, { type AutomationRule } from './AutomationRulesPanel'

afterEach(() => { cleanup(); get.mockReset(); put.mockReset() })

const existing: AutomationRule = {
  id: 'abc123def456', name: 'ETA minęło', enabled: true, condition: 'eta_passed', days: 3, status: null, notify: 'watchers',
}
const response = (rules: AutomationRule[]) => ({
  rules, conditions: ['eta_passed', 'notify_soon_status', 'no_driver', 'plan_unconfirmed'],
  statuses: ['W_PORCIE', 'ODPRAWA', 'AWIZOWANY'], max_rules: 2,
})

describe('kreator reguł', () => {
  it('admin: nowa reguła, etap dla warunku „przed etapem”, podgląd i zapis całej listy', async () => {
    get.mockImplementation((url: string) => Promise.resolve(url.includes('preview')
      ? { count: 12, sample: [{ id: 1, container_no: 'MSCU1234565' }] } : response([existing])))
    put.mockImplementation((_url: string, body: { rules: AutomationRule[] }) => Promise.resolve(
      response(body.rules.map((r, i) => ({ ...r, id: r.id || `nowa${i}` })))))
    render(<AutomationRulesPanel canEdit />)
    expect(await screen.findByDisplayValue('ETA minęło')).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: 'Dodaj regułę' }))
    expect((screen.getByRole('button', { name: 'Dodaj regułę' }) as HTMLButtonElement).disabled).toBe(true)  // limit 2
    const added = within(screen.getAllByTestId('auto-rule')[1])
    fireEvent.change(added.getByLabelText('Nazwa'), { target: { value: 'Za wolno do awizacji' } })
    fireEvent.change(added.getByLabelText('Warunek'), { target: { value: 'notify_soon_status' } })
    expect((added.getByLabelText('Etap') as HTMLSelectElement).value).toBe('ODPRAWA')
    fireEvent.change(added.getByLabelText('Dni'), { target: { value: '4' } })
    expect(added.getByText(/Awizacja w ciągu 4 dni, a kontener jest jeszcze przed etapem/)).toBeTruthy()

    fireEvent.click(added.getByRole('button', { name: 'Podgląd' }))
    expect((await added.findByRole('status')).textContent).toBe('Dziś spełnia: 12: MSCU1234565…')
    expect(get).toHaveBeenLastCalledWith('/api/automations/rules/preview?condition=notify_soon_status&days=4&status=ODPRAWA')

    fireEvent.click(screen.getByRole('button', { name: 'Zapisz reguły' }))
    expect(await screen.findByText('Reguły zapisane.')).toBeTruthy()
    const sent = put.mock.calls[0][1].rules
    expect(sent).toHaveLength(2)
    expect(sent[1]).toMatchObject({ name: 'Za wolno do awizacji', condition: 'notify_soon_status', days: 4, status: 'ODPRAWA' })
  })

  it('kanały reguły: wybór, ostatni kanał zostaje, zapis (US-063)', async () => {
    get.mockResolvedValue({ ...response([existing]), channels: ['bell', 'email', 'teams', 'n8n'] })
    put.mockImplementation((_url: string, body: { rules: AutomationRule[] }) => Promise.resolve(response(body.rules)))
    render(<AutomationRulesPanel canEdit />)
    const rule = within(await screen.findByTestId('auto-rule'))
    expect(rule.getByText(/\(dzwonek, e-mail, Teams, n8n\)/)).toBeTruthy()      // stara reguła = wszystkie kanały
    for (const name of ['dzwonek', 'e-mail', 'Teams']) fireEvent.click(rule.getByLabelText(name))
    const n8n = rule.getByLabelText('n8n') as HTMLInputElement
    expect(n8n.checked && n8n.disabled).toBe(true)
    expect(rule.getByText(/\(n8n\)/)).toBeTruthy()
    fireEvent.click(rule.getByLabelText('Teams'))
    fireEvent.click(screen.getByRole('button', { name: 'Zapisz reguły' }))
    expect(await screen.findByText('Reguły zapisane.')).toBeTruthy()
    expect(put.mock.calls[0][1].rules[0].channels).toEqual(['teams', 'n8n'])
  })

  it('odmowa zapisu widoczna; usunięcie reguły', async () => {
    get.mockResolvedValue(response([existing]))
    put.mockRejectedValue(new Error('najwyżej 20 reguł'))
    render(<AutomationRulesPanel canEdit />)
    await screen.findByDisplayValue('ETA minęło')
    fireEvent.click(screen.getByRole('button', { name: 'Usuń' }))
    expect(screen.getByText('Brak reguł.')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Zapisz reguły' }))
    expect(await screen.findByText('najwyżej 20 reguł')).toBeTruthy()
    expect(put.mock.calls[0][1]).toEqual({ rules: [] })
  })

  it('logistyka: tylko odczyt i podgląd, bez edycji', async () => {
    get.mockResolvedValue(response([existing]))
    render(<AutomationRulesPanel canEdit={false} />)
    expect(await screen.findByText('ETA minęło')).toBeTruthy()
    expect(screen.getByText('Reguły zmienia administrator.')).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'Zapisz reguły' })).toBeNull()
    expect(screen.getByText(/ETA minęło co najmniej 3 dni temu/)).toBeTruthy()
  })
})
