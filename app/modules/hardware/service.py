"""
Hardware Peripherals Discovery & Physical Barcode Scanner Integration Service
Provides real-time discovery and serial communication for USB Barcode Scanners (Virtual COM / Serial / HID).
"""

import sys
import time
import asyncio
import threading
import subprocess
from typing import Dict, Any, Optional

from app.core.logging import logger
from app.modules.support.service import sio

try:
    import serial
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except ImportError:
    HAS_PYSERIAL = False

_scanner_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_main_event_loop: Optional[asyncio.AbstractEventLoop] = None

# In-memory cached scanner status
_cached_scanner_status: Dict[str, Any] = {
    "connected": False,
    "working": "DISCONNECTED",
    "port": None,
    "device": None,
    "type": None,
    "lastChecked": 0
}


def find_connected_scanner() -> Dict[str, Any]:
    """
    Scans host OS peripherals to detect physical barcode scanners.
    Checks USB Virtual COM Ports (e.g. COM4 with VID 9901 or usbser)
    and Windows PnP POSBarcodeScanner/HID entities.
    """
    global _cached_scanner_status

    now = time.time()
    # Cache result for 5 seconds to avoid excessive hardware polling
    if now - _cached_scanner_status.get("lastChecked", 0) < 5.0:
        return _cached_scanner_status

    # 1. Probe Serial / USB COM Ports
    if HAS_PYSERIAL:
        try:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                desc = (p.description or "").lower()
                hwid = (p.hwid or "").upper()
                name = (p.name or "").lower()

                is_scanner_com = (
                    p.vid == 0x9901 or
                    p.pid == 0x0303 or
                    "VID_9901" in hwid or
                    "VID:PID=9901" in hwid or
                    "barcode" in desc or
                    "scanner" in desc or
                    "usb serial device" in desc or
                    "usb-serial" in desc
                )

                if is_scanner_com:
                    status = {
                        "connected": True,
                        "working": "OK",
                        "port": p.device,
                        "device": p.description,
                        "hwid": p.hwid,
                        "type": "serial_com",
                        "lastChecked": now
                    }
                    _cached_scanner_status = status
                    return status
        except Exception as e:
            logger.debug(f"[hardware-service] Serial port probe notice: {e}")

    # 2. Probe physically PRESENT Windows PnP / HID Devices via SetupAPI (DIGCF_PRESENT only)
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            setupapi = ctypes.windll.setupapi
            cfgmgr32 = ctypes.windll.cfgmgr32

            DIGCF_PRESENT = 0x00000002
            DIGCF_ALLCLASSES = 0x00000004

            class SP_DEVINFO_DATA(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("ClassGuid", ctypes.c_byte * 16),
                    ("DevInst", wintypes.DWORD),
                    ("Reserved", wintypes.ULONG)
                ]

            hdev = setupapi.SetupDiGetClassDevsW(None, None, None, DIGCF_ALLCLASSES | DIGCF_PRESENT)
            if hdev and hdev != -1:
                devinfo = SP_DEVINFO_DATA()
                devinfo.cbSize = ctypes.sizeof(SP_DEVINFO_DATA)
                idx = 0
                buf = ctypes.create_unicode_buffer(1024)
                dev_id_buf = ctypes.create_unicode_buffer(1024)

                while setupapi.SetupDiEnumDeviceInfo(hdev, idx, ctypes.byref(devinfo)):
                    idx += 1
                    dev_id = ""
                    if cfgmgr32.CM_Get_Device_IDW(devinfo.DevInst, dev_id_buf, 1024, 0) == 0:
                        dev_id = dev_id_buf.value

                    prop_type = wintypes.DWORD()
                    name = ""
                    # SPDRP_FRIENDLYNAME = 0x0000000C
                    if setupapi.SetupDiGetDeviceRegistryPropertyW(hdev, ctypes.byref(devinfo), 0x0000000C, ctypes.byref(prop_type), ctypes.byref(buf), 1024, None):
                        name = buf.value
                    # SPDRP_DEVICEDESC = 0x00000000
                    elif setupapi.SetupDiGetDeviceRegistryPropertyW(hdev, ctypes.byref(devinfo), 0x00000000, ctypes.byref(prop_type), ctypes.byref(buf), 1024, None):
                        name = buf.value

                    combo = f"{dev_id} {name}".lower()
                    if any(k in combo for k in [
                        "vid_9901", "vid:pid=9901", "posbarcodescanner", "honeywell",
                        "zebra", "symbol", "netum", "datalogic", "tera", "eyoyo",
                        "inateck", "symcode"
                    ]):
                        setupapi.SetupDiDestroyDeviceInfoList(hdev)
                        status = {
                            "connected": True,
                            "working": "OK",
                            "port": None,
                            "device": name or dev_id,
                            "hwid": dev_id,
                            "type": "pnp_entity",
                            "lastChecked": now
                        }
                        _cached_scanner_status = status
                        return status

                setupapi.SetupDiDestroyDeviceInfoList(hdev)
        except Exception as e:
            logger.debug(f"[hardware-service] SetupAPI probe notice: {e}")

    # 3. No physical scanner device found
    status = {
        "connected": False,
        "working": "DISCONNECTED",
        "port": None,
        "device": None,
        "type": None,
        "lastChecked": now
    }
    _cached_scanner_status = status
    return status


def _scanner_serial_worker():
    """
    Background worker daemon that attaches to the scanner's serial port (COM4)
    and streams scanned barcodes directly to connected web & electron clients.
    """
    global _main_event_loop, _stop_event

    logger.info("[hardware-service] Barcode scanner serial listener worker started.")
    last_connected_state = None

    while not _stop_event.is_set():
        scanner_info = find_connected_scanner()
        current_connected = scanner_info.get("connected", False)

        # Broadcast hardware status change via Socket.IO if changed
        if current_connected != last_connected_state:
            last_connected_state = current_connected
            if _main_event_loop and not _main_event_loop.is_closed():
                try:
                    asyncio.run_coroutine_threadsafe(
                        sio.emit("SCANNER_HARDWARE_STATUS", scanner_info),
                        _main_event_loop
                    )
                except Exception:
                    pass

        port = scanner_info.get("port")
        if current_connected and port and HAS_PYSERIAL:
            try:
                # Open Serial port with short timeout so we can exit cleanly
                with serial.Serial(port, baudrate=9600, timeout=1.0) as ser:
                    logger.info(f"[hardware-service] ✓ Opened barcode scanner serial port: {port}")
                    while not _stop_event.is_set():
                        # Read raw scan line
                        line = ser.readline()
                        if line:
                            raw_str = line.decode("utf-8", errors="ignore").strip()
                            if len(raw_str) >= 2:
                                logger.info(f"[hardware-service] 🟢 Barcode scanned on {port}: {raw_str}")
                                if _main_event_loop and not _main_event_loop.is_closed():
                                    asyncio.run_coroutine_threadsafe(
                                        sio.emit("BARCODE_SCANNED", {
                                            "rawBarcode": raw_str,
                                            "source": "hardware_serial",
                                            "port": port,
                                            "timestamp": int(time.time() * 1000)
                                        }),
                                        _main_event_loop
                                    )
            except Exception as e:
                logger.debug(f"[hardware-service] Notice on serial port {port}: {e}")
                time.sleep(2)
        else:
            time.sleep(2)

    logger.info("[hardware-service] Barcode scanner serial listener worker stopped.")


def start_hardware_monitoring(loop: asyncio.AbstractEventLoop):
    """
    Initializes the hardware monitoring thread within the ASGI event loop lifecycle.
    """
    global _scanner_thread, _stop_event, _main_event_loop

    _main_event_loop = loop
    _stop_event.clear()

    if _scanner_thread is None or not _scanner_thread.is_alive():
        _scanner_thread = threading.Thread(
            target=_scanner_serial_worker,
            name="BarcodeScannerSerialWorker",
            daemon=True
        )
        _scanner_thread.start()


def stop_hardware_monitoring():
    """
    Stops background hardware worker threads on application shutdown.
    """
    global _stop_event, _scanner_thread
    _stop_event.set()
    if _scanner_thread and _scanner_thread.is_alive():
        _scanner_thread.join(timeout=1.0)
    _scanner_thread = None
