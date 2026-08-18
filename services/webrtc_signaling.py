"""
Legacy Re-Export Wrapper for WebRTC Signaling Service
"""

from app.modules.support.service import (
    sio,
    active_calls,
    connected_clients,
    call_queue,
    online_operators,
    online_kiosks,
    get_operator_info,
    get_longest_idle_available_operator,
    dispatch_call_to_operator,
    check_and_dispatch_queued_calls,
    broadcast_admin_telemetry,
    auto_save_support_call,
    get_recordings_dir
)

__all__ = [
    "sio",
    "active_calls",
    "connected_clients",
    "call_queue",
    "online_operators",
    "online_kiosks",
    "get_operator_info",
    "get_longest_idle_available_operator",
    "dispatch_call_to_operator",
    "check_and_dispatch_queued_calls",
    "broadcast_admin_telemetry",
    "auto_save_support_call",
    "get_recordings_dir"
]
