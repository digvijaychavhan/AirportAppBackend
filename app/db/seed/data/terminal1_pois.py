"""
Terminal 1 3D map day-zero POI seed data.

The coordinate formulas intentionally mirror the frontend implementation in
frontend/components/terminal1-3d/terminal1-data.ts and layout-transform.ts.
Database category names remain compatible with the existing directory API;
map_category contains the singular category used by the 3D map.
"""

import math
from typing import Dict, List, Optional, Sequence, Tuple


MapPoint = Tuple[float, float]

CHECKIN_CENTER: MapPoint = (-18.0, 25.0)
DEPARTURE_CENTER: MapPoint = (20.0, -4.0)
PIER_ORIGIN: MapPoint = (9.0, -18.0)
PIER_ROTATION = 2.24

DB_CATEGORY = {
    "gate": "gates",
    "retail": "shopping",
    "food": "dining",
    "amenity": "amenities",
    "service": "services",
}

CATEGORY_ICON = {
    "gate": "flight_takeoff",
    "retail": "shopping_bag",
    "food": "restaurant",
    "amenity": "accessible",
    "service": "info",
}

SECTION_FLOOR = {
    "checkin": "Check-in",
    "departure": "Departure Level",
    "piers": "Departure Piers",
}


def _checkin_point(x: float, z: float) -> MapPoint:
    return CHECKIN_CENTER[0] + x, CHECKIN_CENTER[1] + z


def _pier_point(x: float, z: float) -> MapPoint:
    cos = math.cos(PIER_ROTATION)
    sin = math.sin(PIER_ROTATION)
    return (
        PIER_ORIGIN[0] + cos * x + sin * z,
        PIER_ORIGIN[1] - sin * x + cos * z,
    )


def _rotation_for_line(start: MapPoint, end: MapPoint) -> float:
    return math.atan2(-(end[1] - start[1]), end[0] - start[0])


def _round_point(point: MapPoint) -> MapPoint:
    return round(point[0], 6), round(point[1], 6)


def _record(
    *,
    poi_id: str,
    name: str,
    code: str,
    category: str,
    section: str,
    position: MapPoint,
    approach: MapPoint,
    side: str,
    icon: Optional[str] = None,
    rotation: float = 0.0,
    block: Optional[Tuple[float, float]] = None,
    sub_category: Optional[str] = None,
) -> Dict:
    position = _round_point(position)
    approach = _round_point(approach)
    width = block[0] if block else None
    depth = block[1] if block else None
    db_category = DB_CATEGORY[category]
    return {
        "id": poi_id,
        "name": name,
        "category": db_category,
        "sub_category": sub_category or category,
        "description": "",
        "operating_hours": "24 Hours",
        "terminal": "Terminal 1",
        "floor_name": SECTION_FLOOR[section],
        "gate": f"Gate {code}" if category == "gate" else "",
        "distance_m": 0,
        "badge_label": None,
        "badge_variant": None,
        "image_url": None,
        "x_coord": position[0],
        "y_coord": position[1],
        "is_active": True,
        "map_code": code,
        "map_category": category,
        "map_section": section,
        "map_icon": icon or CATEGORY_ICON[category],
        "map_x": position[0],
        "map_z": position[1],
        "approach_x": approach[0],
        "approach_z": approach[1],
        "map_side": side,
        "map_rotation": rotation,
        "block_width": width,
        "block_depth": depth,
        "map_source": "terminal1-3d-day-zero",
    }


def _checkin_pois() -> List[Dict]:
    entries = [
        ("checkin-retail-1", "1", "Neo Travel", "retail", "shopping_bag", (13, 6.5), (13, 4.9), "south", (3.5, 1.6), "convenience"),
        ("checkin-service-2", "2", "En-wrap (Baggage Wrap)", "service", "luggage", (8, 6.5), (8, 4.9), "south", (3.5, 1.6), "baggage"),
        ("checkin-food-3", "3", "TWC", "food", "restaurant", (3, 6.5), (3, 4.9), "south", (3.5, 1.6), "cafe"),
        ("checkin-business-class", "BC", "Business Class Check-in", "service", "workspace_premium", (19, -5.5), (16.8, -5.5), "east", (3, 2), "assistance"),
        ("checkin-security", "SEC", "Domestic Security Check", "service", "security", (10, -11), (10, -8.7), "center", None, "assistance"),
        ("checkin-information", "i", "Information Desk", "service", "info", (8, 3.5), (6.3, 3.5), "center", None, "assistance"),
        ("checkin-water", "W", "Drinking Water", "amenity", "water_drop", (-20, 1.5), (-18.2, 1.5), "west", None, "water"),
        ("checkin-baby-care", "BC", "Baby Care", "amenity", "baby_changing_station", (20, 1.5), (18.2, 1.5), "east", None, "babycare"),
        ("checkin-prm-toilet", "PRM", "Accessible Toilet", "amenity", "accessible", (-20, -5), (-18.2, -5), "west", None, "accessible"),
        ("checkin-toilets", "WC", "Toilets", "amenity", "wc", (20, -5), (18.2, -7), "east", None, "restroom"),
    ]
    return [
        _record(
            poi_id=poi_id,
            code=code,
            name=name,
            category=category,
            section="checkin",
            position=_checkin_point(*position),
            approach=_checkin_point(*approach),
            side=side,
            icon=icon,
            block=block,
            sub_category=sub_category,
        )
        for poi_id, code, name, category, icon, position, approach, side, block, sub_category in entries
    ]


DEPARTURE_BUSINESSES = [
    (1, "Armani Exchange", "retail"),
    (2, "Helios Luxe", "retail"),
    (4, "Street Burger", "food"),
    (5, "The Irish House", "food"),
    (6, "Chanel", "retail"),
    (7, "Croma", "retail"),
    (8, "Hamleys", "retail"),
    (9, "Miniso", "retail"),
    (10, "Encalm SPA", "retail"),
    (11, "Hello Mercato!", "food"),
    (12, "Accessorize London", "retail"),
    (13, "W", "retail"),
    (14, "BIBA", "retail"),
    (15, "Skechers", "retail"),
    (16, "Hush Puppies", "retail"),
    (17, "Da Milano", "retail"),
    (18, "Hidesign", "retail"),
    (19, "VIP", "retail"),
    (20, "Chocobay", "food"),
    (21, "Mishtaan", "food"),
    (22, "Relay", "retail"),
    (23, "Apollo Pharmacy", "retail"),
    (24, "Encalm Lounge", "retail"),
    (25, "Express by Idli.com", "food"),
    (26, "Masala Kitchen", "food"),
    (27, "Tim Hortons", "food"),
    (28, "Artport", "retail"),
    (29, "Bodyshop", "retail"),
    (30, "Forest Essentials", "retail"),
    (31, "Olfactive", "retail"),
    (32, "L'Occitane", "retail"),
    (33, "Runway", "retail"),
    (34, "Nappa Dori", "retail"),
    (35, "Swarovski", "retail"),
    (36, "Shoppers Stop", "retail"),
]


def _departure_position(code: int) -> Tuple[MapPoint, MapPoint, str, float, Tuple[float, float]]:
    if code in (1, 2, 4, 5):
        codes: Sequence[int] = (1, 2, 4, 5)
        start, end, side, block = (10, 8.2), (32, 6.5), "south", (5, 2.1)
    elif code <= 11:
        codes = (6, 7, 8, 9, 10, 11)
        start, end, side, block = (35, 4.5), (41, -6.4), "east", (2.05, 2.3)
    elif code <= 24:
        codes = tuple(range(12, 25))
        start, end, side, block = (36, -10.7), (14, -17.4), "north", (1.8, 2.2)
    elif code <= 27:
        codes = (25, 26, 27)
        start, end, side, block = (11, -16.8), (2.2, -12), "north", (3.1, 2.1)
    else:
        codes = tuple(range(28, 37))
        start, end, side, block = (2, -9), (2, 6), "west", (1.55, 2.6)

    progress = 0 if len(codes) == 1 else codes.index(code) / (len(codes) - 1)
    position = (
        start[0] + (end[0] - start[0]) * progress,
        start[1] + (end[1] - start[1]) * progress,
    )
    toward_center = (DEPARTURE_CENTER[0] - position[0], DEPARTURE_CENTER[1] - position[1])
    distance = math.hypot(*toward_center)
    approach_offset = block[1] / 2 + 1.05
    approach = (
        position[0] + toward_center[0] / distance * approach_offset,
        position[1] + toward_center[1] / distance * approach_offset,
    )
    rotation = _rotation_for_line(start, end)
    return position, approach, side, rotation, block


def _departure_business_pois() -> List[Dict]:
    records = []
    for code, name, category in DEPARTURE_BUSINESSES:
        position, approach, side, rotation, block = _departure_position(code)
        records.append(_record(
            poi_id=f"departure-{category}-{code}",
            code=str(code),
            name=name,
            category=category,
            section="departure",
            position=position,
            approach=approach,
            side=side,
            rotation=rotation,
            block=block,
        ))
    return records


DEPARTURE_AMENITIES = [
    ("departure-info", "i", "Information Desk with Wi-Fi", "service", "info", (22, -10), (20, -9), "center", "assistance"),
    ("departure-lift", "L", "Lift", "amenity", "elevator", (7, -7), (9, -6.5), "west", "transit"),
    ("departure-escalator", "E", "Escalator", "amenity", "escalator", (30, -11), (28, -10), "east", "transit"),
    ("departure-toilets", "WC", "Toilets", "amenity", "wc", (36, -12), (34, -7.5), "east", "restroom"),
    ("departure-prm", "PRM", "PRM Toilet", "amenity", "accessible", (10, -13), (12, -12), "north", "accessible"),
    ("departure-water", "W", "Drinking Water", "amenity", "water_drop", (34, -1), (32, -1), "east", "water"),
    ("departure-smoking", "S", "Smoking Area", "amenity", "smoking_rooms", (38, -4), (35.5, -4), "east", "smoking"),
    ("departure-food-court", "FC", "Food Court Connection", "food", "restaurant", (31, -8), (29, -7), "east", "food"),
    ("departure-gates-27-36", "27–36", "Towards Gates 27–36", "gate", "flight_takeoff", (4, -13.5), (6, -12), "north", "gate"),
    ("departure-bus-gates", "31–45", "Towards Bus Gates 31–45", "gate", "directions_bus", (27, -15.5), (26, -11.5), "north", "gate"),
]


def _departure_amenity_pois() -> List[Dict]:
    return [
        _record(
            poi_id=poi_id,
            code=code,
            name=name,
            category=category,
            section="departure",
            position=position,
            approach=approach,
            side=side,
            icon=icon,
            sub_category=sub_category,
        )
        for poi_id, code, name, category, icon, position, approach, side, sub_category in DEPARTURE_AMENITIES
    ]


PIER_BUSINESSES = [
    (1, "Masala Kitchen", "food", (3, -4.9), "north"),
    (2, "Idli Express", "food", (5.8, -4.9), "north"),
    (3, "Dolce Torino", "food", (11, -4.9), "north"),
    (4, "Mishtaan", "retail", (14, -4.9), "north"),
    (5, "Momo Express", "food", (18, 4.9), "south"),
    (6, "Barista", "food", (21, 4.9), "south"),
    (7, "Patanjali", "retail", (24, 4.9), "south"),
    (9, "Guardian Pharmacy", "retail", (30, -4.9), "north"),
    (10, "Sugar & Spice", "food", (33, -4.9), "north"),
    (11, "Burger Pizza", "food", (36, 4.9), "south"),
    (12, "Mishtaan", "retail", (39, 4.9), "south"),
    (13, "Delhi Cafeccino", "food", (48, -4.9), "north"),
    (14, "Flying Bites", "food", (53, 4.9), "south"),
]


def _pier_business_pois() -> List[Dict]:
    records = []
    for code, name, category, (x, z), side in PIER_BUSINESSES:
        approach_z = -3 if side == "north" else 3
        records.append(_record(
            poi_id=f"piers-{category}-{code}",
            code=str(code),
            name=name,
            category=category,
            section="piers",
            position=_pier_point(x, z),
            approach=_pier_point(x, approach_z),
            side=side,
            rotation=PIER_ROTATION,
            block=(2.8, 1.45),
        ))
    return records


def _pier_gate_pois() -> List[Dict]:
    records = []
    for gate_number in range(2, 24):
        north = gate_number % 2 == 1
        x = 2.8 + ((gate_number - 2) // 2) * 5.45
        position_z = -8.5 if north else 8.5
        approach_z = -6.25 if north else 6.25
        code = f"{gate_number:02d}"
        records.append(_record(
            poi_id=f"gate-{code}",
            code=code,
            name=f"Gate {code}",
            category="gate",
            section="piers",
            position=_pier_point(x, position_z),
            approach=_pier_point(x, approach_z),
            side="north" if north else "south",
            rotation=PIER_ROTATION,
        ))
    return records


PIER_AMENITIES = [
    ("piers-toilets-west", "WC", "Toilets — Near Gates 05–07", "wc", (13, -2.8), (11.5, -1.5), "north", "restroom"),
    ("piers-prm", "PRM", "PRM Toilet", "accessible", (31, 2.8), (29.5, 1.4), "south", "accessible"),
    ("piers-water", "W", "Drinking Water", "water_drop", (48, -2.8), (46.5, -1.4), "north", "water"),
    ("piers-travelator", "T", "Travelator", "moving_walkway", (38, 0), (36.5, 0), "center", "transit"),
]


def _pier_amenity_pois() -> List[Dict]:
    return [
        _record(
            poi_id=poi_id,
            code=code,
            name=name,
            category="amenity",
            section="piers",
            position=_pier_point(*position),
            approach=_pier_point(*approach),
            side=side,
            icon=icon,
            rotation=PIER_ROTATION,
            sub_category=sub_category,
        )
        for poi_id, code, name, icon, position, approach, side, sub_category in PIER_AMENITIES
    ]


def get_seed_terminal1_pois() -> List[Dict]:
    """Return the 96 Terminal 1 3D map day-zero POIs."""
    return (
        _checkin_pois()
        + _departure_business_pois()
        + _departure_amenity_pois()
        + _pier_business_pois()
        + _pier_gate_pois()
        + _pier_amenity_pois()
    )


TERMINAL1_POI_IDS = {poi["id"] for poi in get_seed_terminal1_pois()}
