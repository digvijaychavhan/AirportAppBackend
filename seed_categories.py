from database import engine, Base, SessionLocal
import models

# Recreate tables (this will add wayfinding_categories)
Base.metadata.create_all(engine)

db = SessionLocal()

CATEGORIES = [
  {
    "id": "shopping",
    "title": "Shopping",
    "description": "Explore shops and\nretail stores",
    "photo_url": "/findway-shopping.png",
    "icon": "shopping_bag",
    "icon_color": "#2563EB",
    "icon_bg": "#DBEAFE",
    "route": "/wayfinding/shopping",
  },
  {
    "id": "dining",
    "title": "Eat & Dine",
    "description": "Restaurants, cafes\nand fast food",
    "photo_url": "/findway-dining.png",
    "icon": "restaurant",
    "icon_color": "#D97706",
    "icon_bg": "#FEF3C7",
    "route": "/eat-dine",
  },
  {
    "id": "services",
    "title": "Services",
    "description": "Assistance, counters\nand other services",
    "photo_url": "/findway-services.png",
    "icon": "support_agent",
    "icon_color": "#7C3AED",
    "icon_bg": "#EDE9FE",
    "route": "/wayfinding/services",
  },
  {
    "id": "gates",
    "title": "Boarding Gates",
    "description": "Find your boarding gates\nand directions",
    "photo_url": "/findway-gates.png",
    "icon": "flight_takeoff",
    "icon_color": "#059669",
    "icon_bg": "#D1FAE5",
    "route": "/wayfinding/gates",
  },
  {
    "id": "lounges",
    "title": "Lounges",
    "description": "Airport lounges and\nrelaxation areas",
    "photo_url": "/findway-lounge.png",
    "icon": "weekend",
    "icon_color": "#DB2777",
    "icon_bg": "#FCE7F3",
    "route": "/wayfinding/lounges",
  },
  {
    "id": "amenities",
    "title": "Airport Amenities",
    "description": "Facilities like restrooms,\nprayer rooms and more",
    "photo_url": "/findway-amenities.png",
    "icon": "wc",
    "icon_color": "#0891B2",
    "icon_bg": "#CFFAFE",
    "route": "/wayfinding/amenities",
  },
]

for cat_data in CATEGORIES:
    existing = db.query(models.WayfindingCategory).filter(models.WayfindingCategory.id == cat_data["id"]).first()
    if not existing:
        cat = models.WayfindingCategory(**cat_data)
        db.add(cat)

db.commit()
db.close()
print("Database migrated and seeded successfully.")
