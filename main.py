"""
Airport Helpdesk ASGI Root Entrypoint
Exports combined_app for Uvicorn multi-worker deployments, systemd, and Docker.
"""

from app.main import combined_app, fastapi_app, app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:combined_app", host="0.0.0.0", port=5000, reload=True)
