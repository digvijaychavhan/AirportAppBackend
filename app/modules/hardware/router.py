"""
Hardware Diagnostics & Peripherals REST Router
Exposes live host OS hardware detection endpoints for Barcode Scanners, Cameras, and System metrics.
"""

from fastapi import APIRouter
from app.modules.hardware.service import find_connected_scanner

router = APIRouter(tags=["Hardware Diagnostics"])


@router.get("/api/v1/hardware/scanner")
async def get_scanner_hardware_status():
    """
    Returns live hardware connectivity status of physical barcode readers
    (checks USB Virtual COM serial ports & Windows PnP devices).
    """
    status = find_connected_scanner()
    return {
        "success": True,
        "data": status
    }


@router.get("/api/v1/hardware/status")
async def get_all_hardware_status():
    """
    Returns comprehensive hardware diagnostics for the host machine.
    """
    scanner_status = find_connected_scanner()
    return {
        "success": True,
        "data": {
            "scanner": scanner_status,
            "host": {
                "scannerConnected": scanner_status.get("connected", False),
                "scannerWorking": scanner_status.get("working", "DISCONNECTED"),
                "scannerPort": scanner_status.get("port"),
                "scannerDevice": scanner_status.get("device")
            }
        }
    }
