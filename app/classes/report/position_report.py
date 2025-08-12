from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from app.utils.time_utils import get_current_timestamp

class PositionKind(Enum):
    NONE = "NONE"
    NAVAID = "NAVAID"
    AIRPORT = "AIRPORT"
    FIX = "FIX"
    LAT_LON = "LAT/LON"
    PLACE_BEARING_DIST = "PLACE/BEARING/DIST"

class Turbulence(Enum):
    LIGHT = 0
    MODERATE = 1
    SEVERE = 2

class Icing(Enum):
    TRACE = 0
    LIGHT = 1
    MODERATE = 2
    SEVERE = 3

class VerticalDirection(Enum):
    UP = 0
    DOWN = 1

TimeSec     = int      # secondes
AltitudeFt  = int      # pieds
Degrees     = int      # 0..360
SpeedKmH    = int      # km/h
DistanceKm  = float    # km
FuelKg      = float    # kg

@dataclass
class PlaceBearingDist:
    place_ident: str
    bearing_deg: Degrees
    distance_km: DistanceKm  

@dataclass
class Position:
    kind: PositionKind
    navaid: Optional[str] = None
    airport: Optional[str] = None
    fix: Optional[str] = None
    lat_lon: Optional[Tuple[float, float]] = None  # (lat, lon) en degrés
    pbd: Optional[PlaceBearingDist] = None

@dataclass
class Winds:
    winddirection_deg: Degrees
    speed_kmh: SpeedKmH           # plus de CHOICE, toujours km/h

@dataclass
class VerticalChange:
    verticaldirection: VerticalDirection
    verticalrate_mps: float       # m/s (au lieu de ft/min); simple et cohérent avec "sec"

Positioncurrent = Position
Fixnext = Position
Fixnextplusone = Position
Reportedwaypointposition = Position
Reportedwaypointtime_sec = TimeSec
Reportedwaypointaltitude_ft = AltitudeFt

@dataclass
class PositionReport:
    positioncurrent: Positioncurrent
    timeatpositioncurrent_sec: TimeSec
    altitude_ft: AltitudeFt
    fixnext: Optional[Fixnext] = None
    timeatafixnext_sec: Optional[TimeSec] = None
    fixnextplusone: Optional[Fixnextplusone] = None
    timeatedestination_sec: Optional[TimeSec] = None
    remainingfuel_kg: Optional[FuelKg] = None
    temperature_c: Optional[int] = None
    winds: Optional[Winds] = None
    turbulence: Optional[Turbulence] = None
    icing: Optional[Icing] = None
    speed_kmh: Optional[SpeedKmH] = None
    speedground_kmh: Optional[SpeedKmH] = None
    verticalchange: Optional[VerticalChange] = None
    trackangle_deg: Optional[Degrees] = None
    trueheading_deg: Optional[Degrees] = None
    distance_km: Optional[DistanceKm] = None
    supplementaryinformation: Optional[str] = None
    reportedwaypointposition: Optional[Reportedwaypointposition] = None
    reportedwaypointtime_sec: Optional[Reportedwaypointtime_sec] = None
    reportedwaypointaltitude_ft: Optional[Reportedwaypointaltitude_ft] = None
