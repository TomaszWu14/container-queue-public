"""US-016 (P-05): numer telefonu kierowcy w formacie międzynarodowym (E.164).

Numer bez kierunkowego (9 cyfr) dostaje kierunkowy kraju magazynu rozładunku — w Polsce i Portugalii
numery komórkowe mają po 9 cyfr, więc samych cyfr nie da się przypisać do kraju. Brak magazynu albo
kraj spoza listy = Polska (jak dotąd). Numer z „+” albo „00” zostaje taki, jak go podano."""
import re

COUNTRY_PREFIX = {"PL": "+48", "PT": "+351"}
DEFAULT_COUNTRY = "PL"
FORMAT_HINT = "Telefon w formacie +48 600 000 000 albo +351 912 345 678 (E.164)."


def normalize_phone(value: str, country: str | None = DEFAULT_COUNTRY) -> str:
    """Postać E.164; ValueError, gdy to nie numer telefonu."""
    digits = re.sub(r"[\s().-]", "", value or "")
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    if re.fullmatch(r"\d{9}", digits):
        digits = COUNTRY_PREFIX.get((country or "").upper(), COUNTRY_PREFIX[DEFAULT_COUNTRY]) + digits
    if not re.fullmatch(r"\+[1-9]\d{7,14}", digits):
        raise ValueError(FORMAT_HINT)
    return digits


def warehouse_country(container) -> str:
    warehouse = getattr(container, "warehouse", None)
    return (warehouse.country if warehouse and warehouse.country else DEFAULT_COUNTRY)


def phone_for_sms(container) -> str:
    """Numer kierowcy do wysyłki SMS: E.164 wg kraju magazynu; nierozpoznany zostaje bez zmian
    (bramka SMS odrzuci go i panel pokaże błąd wysyłki)."""
    raw = (container.driver_phone or "").strip()
    try:
        return normalize_phone(raw, warehouse_country(container))
    except ValueError:
        return raw
