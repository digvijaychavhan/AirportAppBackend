import logging
from starlette.responses import JSONResponse
from starlette.routing import Route
from database import SessionLocal
from models import WayfindingCategory

logger = logging.getLogger("admin_routes")

async def get_wayfinding_categories(request):
    try:
        db = SessionLocal()
        categories = db.query(WayfindingCategory).order_by(WayfindingCategory.title).all()
        
        data = [{
            "id": cat.id,
            "title": cat.title,
            "description": cat.description,
            "photo": cat.photo_url,
            "icon": cat.icon,
            "iconColor": cat.icon_color,
            "iconBg": cat.icon_bg,
            "route": cat.route,
            "isActive": cat.is_active
        } for cat in categories]
        
        db.close()
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Error fetching wayfinding categories: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

async def create_or_update_category(request):
    try:
        body = await request.json()
        db = SessionLocal()
        
        cat_id = body.get("id")
        
        # Enforce defaults for colors
        icon_color = body.get("iconColor") or "#2563EB"
        icon_bg = body.get("iconBg") or "#DBEAFE"
        
        if cat_id:
            cat = db.query(WayfindingCategory).filter(WayfindingCategory.id == cat_id).first()
            if not cat:
                db.close()
                return JSONResponse({"success": False, "message": "Category not found"}, status_code=404)
        else:
            cat = WayfindingCategory()
            db.add(cat)
            
        cat.title = body.get("title", cat.title)
        cat.description = body.get("description", cat.description)
        cat.photo_url = body.get("photo", cat.photo_url)
        cat.icon = body.get("icon", cat.icon)
        cat.icon_color = icon_color
        cat.icon_bg = icon_bg
        cat.route = body.get("route", cat.route)
        cat.is_active = body.get("isActive", True)
        
        db.commit()
        db.refresh(cat)
        db.close()
        return JSONResponse({"success": True, "message": "Category saved successfully"})
    except Exception as e:
        logger.error(f"Error saving category: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

async def delete_category(request):
    try:
        cat_id = request.path_params.get("id")
        db = SessionLocal()
        cat = db.query(WayfindingCategory).filter(WayfindingCategory.id == cat_id).first()
        if not cat:
            db.close()
            return JSONResponse({"success": False, "message": "Category not found"}, status_code=404)
            
        db.delete(cat)
        db.commit()
        db.close()
        return JSONResponse({"success": True, "message": "Category deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

routes = [
    Route("/api/v1/admin/wayfinding/categories", get_wayfinding_categories, methods=["GET"]),
    Route("/api/v1/admin/wayfinding/categories", create_or_update_category, methods=["POST"]),
    Route("/api/v1/admin/wayfinding/categories/{id}", delete_category, methods=["DELETE"])
]
