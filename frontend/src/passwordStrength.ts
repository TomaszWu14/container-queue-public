// Miernik siły hasła (US-090, ASVS 2.1.8): tylko podpowiedź przy ustawianiu hasła — o przyjęciu hasła
// decyduje serwer (validate_password_policy). Liczy długość, różnorodność znaków i oczywiste wzorce.
export type Strength = 0 | 1 | 2 | 3

const COMMON = ['password', 'haslo', 'qwerty', 'admin', '123456', 'abc123', 'letmein', 'welcome', 'kolejka']

export function passwordStrength(pw: string): Strength {
  if (pw.length < 8) return 0
  const lower = pw.toLowerCase()
  if (COMMON.some(w => lower.includes(w)) || /^(.)\1+$/.test(pw) || /(0123|1234|2345|3456|4567|5678|6789|abcd)/.test(lower)) return 1
  const kinds = [/[a-z]/, /[A-Z]/, /\d/, /[^A-Za-z0-9]/].filter(r => r.test(pw)).length
  const score = (pw.length >= 12 ? 1 : 0) + (pw.length >= 16 ? 1 : 0) + (kinds >= 3 ? 1 : 0)
  return score >= 2 ? 3 : score === 1 ? 2 : 1
}
