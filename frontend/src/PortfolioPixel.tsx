import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

// Piksel portfolio.twapp.pl: przy każdej zmianie ekranu (łącznie z /demo i /login, bo
// komponent wisi poza stanem zalogowania) ładujemy niewidoczny 1x1 GIF, żeby właściciel
// liczył obejrzane ekrany tego demo na swoim portfolio. Błąd sieci nic nie zmienia na ekranie.
export default function PortfolioPixel() {
  const { pathname } = useLocation()
  useEffect(() => {
    new Image().src = 'https://portfolio.twapp.pl/px/kolejka-kontenerow'
  }, [pathname])
  return null
}
