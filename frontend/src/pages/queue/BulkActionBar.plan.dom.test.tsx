// @vitest-environment jsdom
// „Wyślij plan” w pasku akcji masowych (US-017): potwierdzenie, jedno żądanie dla zaznaczonych,
// wynik bez cichego pomijania (brak adresu / błąd poczty / bez spedytora = komunikat błędu).
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'

const { post, toast } = vi.hoisted(() => ({ post: vi.fn(), toast: vi.fn() }))
vi.mock('../../api', () => ({ api: { post }, errorMessage: (e: unknown) => String(e) }))
vi.mock('../../feedback', () => ({ useToast: () => ({ showToast: toast }) }))
vi.mock('../../ConfirmDialog', () => ({ useConfirm: () => ({ confirm: () => Promise.resolve(true) }) }))

import BulkActionBar, { planSummary, type PlanResult } from './BulkActionBar'
import type { QueueMove } from './useQueueMove'

afterEach(() => { cleanup(); post.mockReset(); toast.mockReset() })

const mv = { selected: new Set([7, 9]), setSelected: vi.fn(), bulkDatePick: false,
  setBulkDatePick: vi.fn(), setPendingMove: vi.fn() } as unknown as QueueMove
const result = (over: Partial<PlanResult> = {}): PlanResult => ({ sent: 2, no_forwarder: [], skipped: [],
  emailed: [{ forwarder: 'Spedimex' }], missing_email: [], failed: [], ...over })

const bar = (reload = vi.fn()) => render(<BulkActionBar mv={mv} isAdmin={false} warehouseOptions={[]}
  onAvizo={vi.fn()} onQuote={vi.fn()} reload={reload} />)

describe('kolejka — Wyślij plan', () => {
  it('wysyła zaznaczone kontenery jednym żądaniem i pokazuje, komu poszedł mail', async () => {
    post.mockResolvedValue(result())
    const reload = vi.fn()
    bar(reload)
    fireEvent.click(screen.getByRole('button', { name: /Wyślij plan/ }))
    await waitFor(() => expect(toast).toHaveBeenCalled())
    expect(post).toHaveBeenCalledWith('/api/containers/plan/send', { container_ids: [7, 9] })
    expect(toast).toHaveBeenCalledWith('Plan wysłany: 2 kont. · mail: Spedimex', 'success')
    expect(reload).toHaveBeenCalled()
  })

  it('braki adresu, błąd poczty i kontener bez spedytora są komunikatem błędu', async () => {
    post.mockResolvedValue(result({ sent: 1, emailed: [], missing_email: ['Trans'],
      failed: [{ forwarder: 'Spedimex' }], no_forwarder: ['MSKU1234565'] }))
    bar()
    fireEvent.click(screen.getByRole('button', { name: /Wyślij plan/ }))
    await waitFor(() => expect(toast).toHaveBeenCalled())
    const [message, type] = toast.mock.calls[0]
    expect(type).toBe('error')
    expect(message).toContain('brak adresu e-mail: Trans')
    expect(message).toContain('mail nie wyszedł: Spedimex')
    expect(message).toContain('bez spedytora: MSKU1234565')
  })

  it('podsumowanie pomija puste części', () => {
    const t = (k: string) => ({ sendPlanSent: 'S {n}', sendPlanSkipped: 'P {list}' } as Record<string, string>)[k] ?? k
    expect(planSummary(result({ emailed: [], skipped: ['A'] }), t)).toBe('S 2 · P A')
  })
})
