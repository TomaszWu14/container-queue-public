"""Demo: pozycje statków na mapie śledzenia (zamiast AIS, którego instancja pokazowa nie ma).

Każdy statek z kolejki demo dostaje miejsce na trasie Azja → Europa (przez Malakkę i Suez),
przebytą linię, prędkość, kurs i port docelowy. Ostatni czeka na redzie Gdańska.
Dane zmyślone: MMSI/IMO spoza prawdziwych zakresów (999…, 99…)."""
import datetime as dt
import math

from app.models import TrackedVessel, VesselPosition
from app.tracking.ais import normalize_name
from app.tracking.geo import hours_to_destination

# punkty na morzu (lat, lon): Ningbo → Cieśnina Tajwańska → Singapur → Sri Lanka → Aden → Suez
# → Morze Śródziemne → Gibraltar → Kanał La Manche → Skagen → Gdańsk
ROUTE = [(29.9, 122.2), (24.5, 119.6), (17.0, 114.5), (8.0, 108.0), (1.3, 104.3), (3.0, 100.5),
         (6.0, 94.0), (5.8, 80.5), (11.0, 62.0), (12.6, 47.0), (12.6, 43.3), (20.0, 38.5),
         (27.5, 34.0), (31.4, 32.4), (33.5, 26.0), (37.0, 12.0), (37.0, 1.0), (35.95, -5.6),
         (38.0, -10.0), (44.0, -9.5), (48.8, -5.5), (50.2, -0.5), (52.0, 3.0), (54.5, 6.5),
         (57.9, 10.8), (56.0, 12.7), (55.0, 14.5), (54.6, 18.8)]
# (ułamek trasy, port docelowy, prędkość kn) — kolejno: Morze Południowochińskie, Ocean Indyjski,
# Morze Śródziemne, reda Gdańska (stoi)
PLAN = [(0.12, "GDANSK", 18.4), (0.38, "HAMBURG", 16.9), (0.62, "ROTTERDAM", 17.6),
        (1.0, "GDANSK", 0.3)]
STEPS = 120   # punktów trasy na całą drogę


def _point(frac: float) -> tuple[float, float]:
    """Pozycja w danym ułamku trasy (liniowo między punktami)."""
    pos = frac * (len(ROUTE) - 1)
    i = min(int(pos), len(ROUTE) - 2)
    t = pos - i
    (a_lat, a_lon), (b_lat, b_lon) = ROUTE[i], ROUTE[i + 1]
    return round(a_lat + (b_lat - a_lat) * t, 4), round(a_lon + (b_lon - a_lon) * t, 4)


def _bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dlon = math.radians(b[1] - a[1])
    y = math.sin(dlon) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dlon)
    return round((math.degrees(math.atan2(y, x)) + 360) % 360, 1)


def positions(db, vessel_names: list[str], now: dt.datetime) -> int:
    """Statki z pozycją i przebytą trasą; zwraca liczbę statków."""
    for k, (name, (frac, dest, sog)) in enumerate(zip(vessel_names, PLAN, strict=False)):
        lat, lon = _point(frac)
        trail_steps = max(2, int(frac * STEPS))
        trail = [_point(frac * s / trail_steps) for s in range(trail_steps + 1)]
        hours = hours_to_destination(lat, lon, sog, dest)
        vessel = TrackedVessel(
            name=normalize_name(name), mmsi=999000101 + k, imo=9900101 + k, lat=lat, lon=lon, sog=sog,
            cog=_bearing(trail[-2], trail[-1]), destination=dest,
            ais_eta=now + dt.timedelta(hours=hours if hours is not None else 6),
            last_seen=now - dt.timedelta(minutes=4 + 7 * k),
            near_port=dest if sog < 3 else "", near_port_since=now - dt.timedelta(hours=9) if sog < 3 else None,
            length_m=[366, 334, 300, 399][k % 4], beam_m=[51, 48, 48, 59][k % 4])
        db.add(vessel)
        db.flush()
        # trasa: równe odstępy w czasie, ostatni punkt = teraz (rejs ~5 tygodni na całą drogę)
        span = dt.timedelta(days=35 * frac)
        db.add_all(VesselPosition(vessel_id=vessel.id, lat=p_lat, lon=p_lon,
                                  at=now - span + span * s / trail_steps)
                   for s, (p_lat, p_lon) in enumerate(trail))
    return min(len(vessel_names), len(PLAN))
