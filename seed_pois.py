from database import engine, Base, SessionLocal
from models import Poi
import os

# Delete app.db to recreate fresh tables (quickest way to alter schema locally)
if os.path.exists("app.db"):
    os.remove("app.db")
Base.metadata.create_all(engine)

db = SessionLocal()

EAT_DINE = [
  {
    "id": "poi_r1", "name": "Third Wave Coffee", "category": "eat-dine", "sub_category": "cafe",
    "description": "Specialty coffee, pastries, sandwiches & more", "operating_hours": "6:00 AM – 11:00 PM",
    "terminal": "T3 Departure", "floor_name": "Level 2", "gate": "Near Gate 24", "distance_m": 120,
    "image_url": "/restaurants/third-wave-coffee.png"
  },
  {
    "id": "poi_r2", "name": "McDonald's", "category": "eat-dine", "sub_category": "fastfood",
    "description": "Burgers, fries, beverages and more", "operating_hours": "24 Hours",
    "terminal": "T3 Departure", "floor_name": "Food Court", "gate": "", "distance_m": 150,
    "image_url": "/restaurants/mcdonalds.png"
  },
  {
    "id": "poi_r3", "name": "Bikanervala", "category": "eat-dine", "sub_category": "indian",
    "description": "North Indian snacks, meals & sweets", "operating_hours": "6:00 AM – 11:00 PM",
    "terminal": "T3 Departure", "floor_name": "", "gate": "Near Gate 19", "distance_m": 180,
    "image_url": "/restaurants/bikanervala.png"
  },
  {
    "id": "poi_r4", "name": "Subway", "category": "eat-dine", "sub_category": "fastfood",
    "description": "Sandwiches, salads & wraps", "operating_hours": "6:00 AM – 12:00 AM",
    "terminal": "T3 Departure", "floor_name": "Food Court", "gate": "", "distance_m": 210,
    "image_url": "/restaurants/subway.png"
  },
  {
    "id": "poi_r5", "name": "Sichuan House", "category": "eat-dine", "sub_category": "asian",
    "description": "Chinese cuisine, noodles & rice", "operating_hours": "11:00 AM – 11:00 PM",
    "terminal": "T3 Departure", "floor_name": "", "gate": "Near Gate 32", "distance_m": 260,
    "image_url": "/restaurants/sichuan-house.png"
  }
]

SHOPPING = [
  {
    "id": "poi_s1", "name": "Duty Free", "category": "shopping", "sub_category": "dutyfree",
    "description": "Luxury perfumes, cosmetics, chocolates, liquor and travel exclusives.",
    "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "", "gate": "Near Gate 18",
    "distance_m": 110, "image_url": "/shopping/duty-free.png"
  },
  {
    "id": "poi_s2", "name": "Imagine Store", "category": "shopping", "sub_category": "electronics",
    "description": "Apple products, accessories and premium electronics.",
    "operating_hours": "06:00 AM – 11:00 PM", "terminal": "", "floor_name": "", "gate": "Near Gate 22",
    "distance_m": 150, "image_url": "/shopping/imagine-store.png"
  },
  {
    "id": "poi_s3", "name": "Hidesign", "category": "shopping", "sub_category": "fashion",
    "description": "Leather bags, wallets, backpacks and travel accessories.",
    "operating_hours": "08:00 AM – 10:00 PM", "terminal": "Terminal 3", "floor_name": "", "gate": "Near Gate 30",
    "distance_m": 190, "image_url": "/shopping/hidesign.png"
  },
  {
    "id": "poi_s4", "name": "Relay Books", "category": "shopping", "sub_category": "books",
    "description": "Books, magazines, snacks and travel accessories.",
    "operating_hours": "05:00 AM – 11:00 PM", "terminal": "", "floor_name": "", "gate": "Near Gate 11",
    "distance_m": 220, "image_url": "/shopping/relay-books.png"
  },
  {
    "id": "poi_s5", "name": "Travel Essentials", "category": "shopping", "sub_category": "convenience",
    "description": "Everything you need for your journey.",
    "operating_hours": "24 Hours", "terminal": "", "floor_name": "", "gate": "Near Security Exit",
    "distance_m": 250, "image_url": "/shopping/travel-essentials.png"
  }
]

LOUNGES = [
  {
    "id": "poi_l1", "name": "Encalm Lounge", "category": "lounge", "sub_category": "t3,international,24hr,premium",
    "description": "Premium lounge offering gourmet dining, Wi-Fi, shower facilities and business workstations.",
    "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "", "gate": "Near Gate 15",
    "distance_m": 120, "image_url": "/lounges/encalm-lounge.png", "badge_label": "Premium", "badge_variant": "purple"
  },
  {
    "id": "poi_l2", "name": "Plaza Premium Lounge", "category": "lounge", "sub_category": "t3,international,24hr,business",
    "description": "International lounge with buffet, shower rooms and dedicated business zone.",
    "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "", "gate": "International Departures",
    "distance_m": 180, "image_url": "/lounges/plaza-premium.png", "badge_label": "International", "badge_variant": "teal"
  },
  {
    "id": "poi_l3", "name": "Air India Maharaja Lounge", "category": "lounge", "sub_category": "t3,international,24hr,business",
    "description": "Exclusive lounge for Air India Business and First Class passengers.",
    "operating_hours": "24 Hours", "terminal": "Terminal 3", "floor_name": "", "gate": "Near Gate 22",
    "distance_m": 210, "image_url": "/lounges/maharaja-lounge.png", "badge_label": "Business Class", "badge_variant": "amber"
  },
  {
    "id": "poi_l4", "name": "Travel Club Lounge", "category": "lounge", "sub_category": "t2,domestic",
    "description": "Comfortable lounge with refreshments, Wi-Fi and charging stations.",
    "operating_hours": "05:00 AM – 11:00 PM", "terminal": "Terminal 2", "floor_name": "", "gate": "Near Security",
    "distance_m": 260, "image_url": "/lounges/travel-club.png", "badge_label": "Domestic", "badge_variant": "green"
  },
  {
    "id": "poi_l5", "name": "Premium Lounge", "category": "lounge", "sub_category": "t1,premium,24hr",
    "description": "Quiet premium lounge offering complimentary meals and beverages.",
    "operating_hours": "24 Hours", "terminal": "Terminal 1", "floor_name": "", "gate": "Near Gate 5",
    "distance_m": 300, "image_url": "/lounges/travel-club.png", "badge_label": "VIP", "badge_variant": "red"
  }
]

ALL_POIS = EAT_DINE + SHOPPING + LOUNGES

for item in ALL_POIS:
    poi = Poi(**item)
    db.add(poi)

db.commit()
db.close()
print("POIs seeded successfully.")
