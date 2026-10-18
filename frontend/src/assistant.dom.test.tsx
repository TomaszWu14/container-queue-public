// @vitest-environment jsdom
// Asystent wiedzy (#38): odpowiedź modelu + fakty; bez modelu same fakty z adnotacją;
// US-039: odpowiedź z szablonu oznaczona wprost, przykładowe pytania klikane.
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'

const reply = { current: {} as unknown }
const examples = { current: { questions: [] as string[] } }
vi.mock('./api', () => ({
  api: { post: vi.fn(() => Promise.resolve(reply.current)), get: vi.fn(() => Promise.resolve(examples.current)) },
  errorMessage: (e: unknown) => String(e),
}))

import AssistantBox from './AssistantBox'

const FACTS = { kontenery: [{ kontener: 'MSCU1234567', statek: 'MV DEMO BOREAS', eta: null }], materialy: [] }

async function ask(q: string) {
  fireEvent.change(screen.getByRole('textbox'), { target: { value: q } })
  fireEvent.click(screen.getByRole('button', { name: 'Zapytaj' }))
}

describe('AssistantBox', () => {
  afterEach(() => { cleanup(); examples.current = { questions: [] } })

  it('pokazuje odpowiedź modelu i fakty (puste pola pominięte)', async () => {
    reply.current = { answer: 'Płynie statkiem MV DEMO BOREAS.', facts: FACTS, ai: true }
    render(<AssistantBox />)
    await ask('status MSCU1234567')
    await waitFor(() => screen.getByText('Płynie statkiem MV DEMO BOREAS.'))
    expect(screen.getByText('MSCU1234567')).toBeTruthy()
    expect(screen.queryByText('eta')).toBeNull()
  })

  it('bez modelu: same fakty; brak faktów: komunikat', async () => {
    reply.current = { answer: null, facts: FACTS, ai: false }
    render(<AssistantBox />)
    await ask('MSCU1234567')
    await waitFor(() => screen.getByTestId('as-fact'))
    reply.current = { answer: null, facts: { kontenery: [], materialy: [] }, ai: false }
    await ask('hej')
    await waitFor(() => expect(screen.queryByTestId('as-fact')).toBeNull())
  })

  it('szablon bez modelu: oznaczenie; przykładowe pytanie wysyła się po kliknięciu', async () => {
    examples.current = { questions: ['Jaki jest status MSCU1234567?'] }
    reply.current = { answer: 'Kontener MSCU1234567, bez awizacji.', answer_source: 'template', facts: FACTS, ai: false }
    render(<AssistantBox />)
    fireEvent.click(await screen.findByRole('button', { name: 'Jaki jest status MSCU1234567?' }))
    await waitFor(() => screen.getByText('Kontener MSCU1234567, bez awizacji.'))
    expect(screen.getByTestId('as-template').textContent).toContain('model AI')
    expect((screen.getByRole('textbox') as HTMLInputElement).value).toBe('Jaki jest status MSCU1234567?')
  })
})
