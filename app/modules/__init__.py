"""
Modular Domain Routers Aggregate
"""

from app.modules.flights import flights_router
from app.modules.wayfinding import wayfinding_router
from app.modules.support import support_router
from app.modules.admin import admin_router
from app.modules.wifi import wifi_router
from app.modules.ai import ai_router
from app.modules.feedback import feedback_router
from app.modules.kiosk import kiosk_router

all_routers = [
    flights_router,
    wayfinding_router,
    support_router,
    admin_router,
    wifi_router,
    ai_router,
    feedback_router,
    kiosk_router
]

__all__ = [
    "flights_router",
    "wayfinding_router",
    "support_router",
    "admin_router",
    "wifi_router",
    "ai_router",
    "feedback_router",
    "kiosk_router",
    "all_routers"
]
