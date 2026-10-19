// @vitest-environment jsdom
// US-090: pokaż / ukryj hasło (ASVS 2.1.12) i miernik siły przy ustawianiu hasła (ASVS 2.1.8)
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'

vi.mock('./i18n', () => ({ useT: () => (key: string) => key }))
import PasswordInput from './PasswordInput'
import { passwordStrength } from './passwordStrength'

afterEach(cleanup)

describe('PasswordInput', () => {
  it('przełącza widoczność hasła i mówi to czytnikowi ekranu', () => {
    render(<PasswordInput aria-label="hasło" value="Tajne123" onChange={() => {}} />)
    const input = screen.getByLabelText('hasło') as HTMLInputElement
    expect(input.type).toBe('password')
    const btn = screen.getByRole('button', { name: 'pwShow' })
    fireEvent.click(btn)
    expect(input.type).toBe('text')
    expect(screen.getByRole('button', { name: 'pwHide' }).getAttribute('aria-pressed')).toBe('true')
  })

  it('miernik tylko gdy włączony i jest co oceniać', () => {
    const { rerender } = render(<PasswordInput value="" showStrength onChange={() => {}} />)
    expect(screen.queryByRole('status')).toBeNull()
    rerender(<PasswordInput value="Ciche-Mrowisko-8-Port" showStrength onChange={() => {}} />)
    expect(screen.getByRole('status').textContent).toContain('pwStrength3')
  })
})

describe('passwordStrength', () => {
  it('ocenia długość, różnorodność i oczywiste wzorce', () => {
    expect(passwordStrength('krótkie')).toBe(0)
    expect(passwordStrength('password1')).toBe(1)
    expect(passwordStrength('aaaaaaaaaa')).toBe(1)
    expect(passwordStrength('zxcv12345678')).toBe(1)
    expect(passwordStrength('mrowisko8')).toBe(1)
    expect(passwordStrength('Mrowisko8p')).toBe(2)
    expect(passwordStrength('Ciche-Mrowisko-8-Port')).toBe(3)
  })
})
