"""Ochrona tras publicznych (bez logowania, dostęp po tokenie w ścieżce): awizacja dla spedytora
i link wywołań palet dla magazynu zewnętrznego (DLT). Jedno miejsce — żadna publiczna trasa nie
jest słabszym ogniwem (US-005, R-06): limit żądań na IP i dla POST tylko JSON z naszego Origin."""
from fastapi import Depends, HTTPException, Request, status

from .csrf import origin_allowed
from .security import ApiRateLimiter, client_ip

PUBLIC_LIMIT_PER_MINUTE = 30
_public_limiter = ApiRateLimiter()   # osobny od globalnego — klucz avz:{ip}


def public_limit(request: Request) -> None:
    retry = _public_limiter.hit(f"avz:{client_ip(request)}", PUBLIC_LIMIT_PER_MINUTE)
    if retry is not None:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,
                            "Za dużo żądań. Spróbuj ponownie za chwilę.",
                            headers={"Retry-After": str(int(retry))})


def json_origin_guard(request: Request) -> None:
    """Zamiast tokenu CSRF (brak ciasteczek = brak ambientnych poświadczeń): tylko JSON
    (formularz HTML z obcej strony nie wyśle application/json bez preflightu CORS)
    i Origin/Referer — jeśli jest — musi wskazywać nasz host."""
    if not request.headers.get("content-type", "").lower().startswith("application/json"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Wymagany application/json.")
    source = request.headers.get("origin") or request.headers.get("referer")
    if source and not origin_allowed(request, source):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Niedozwolone źródło żądania.")


PUBLIC = [Depends(public_limit)]
PUBLIC_POST = [Depends(public_limit), Depends(json_origin_guard)]
