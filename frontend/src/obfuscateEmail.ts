// Adres kontaktowy pokazywany jako tekst bez znaku „@” (i bez mailto:) — żeby proste boty
// zbierające adresy nie wyciągały go z HTML-a. Człowiek widzi „jan [at] example.org”.
export const obfuscateEmail = (email: string): string => email.replace('@', ' [at] ')
