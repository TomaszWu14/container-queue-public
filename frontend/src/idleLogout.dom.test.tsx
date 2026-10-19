// @vitest-environment jsdom
import { act, render } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const refresh = vi.fn(() => Promise.resolve(true))
vi.mock('./api', () => ({ refreshSession: () => refresh() }))

import { clearIdleLogout, useIdleLogout, wasIdleLogout } from './idleLogout'

function Probe({ enabled, onIdle }: { enabled: boolean; onIdle: () => void }) {
  useIdleLogout(enabled, 30, onIdle)
  return null
}

describe('useIdleLogout', () => {
  beforeEach(() => { vi.useFakeTimers(); localStorage.clear(); clearIdleLogout(); refresh.mockClear() })
  afterEach(() => vi.useRealTimers())

  it('logs out after 30 minutes without activity and flags the reason', () => {
    const onIdle = vi.fn()
    render(<Probe enabled onIdle={onIdle} />)
    act(() => { vi.advanceTimersByTime(29 * 60_000) })
    expect(onIdle).not.toHaveBeenCalled()
    act(() => { vi.advanceTimersByTime(60_000) })
    expect(onIdle).toHaveBeenCalled()
    expect(wasIdleLogout()).toBe(true)
  })

  it('activity resets the timer and keeps the session alive', () => {
    const onIdle = vi.fn()
    render(<Probe enabled onIdle={onIdle} />)
    act(() => { vi.advanceTimersByTime(20 * 60_000) })
    act(() => { window.dispatchEvent(new Event('keydown')) })
    expect(refresh).toHaveBeenCalledTimes(1)
    act(() => { vi.advanceTimersByTime(20 * 60_000) })
    expect(onIdle).not.toHaveBeenCalled()
  })

  it('does nothing when logged out', () => {
    const onIdle = vi.fn()
    render(<Probe enabled={false} onIdle={onIdle} />)
    act(() => { vi.advanceTimersByTime(60 * 60_000) })
    expect(onIdle).not.toHaveBeenCalled()
  })
})
