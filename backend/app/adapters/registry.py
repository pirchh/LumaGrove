from __future__ import annotations

from app.adapters.base import DeviceAdapter
from app.adapters.errors import DeviceConfigurationError
from app.adapters.shelly import ShellyPlugGen4Adapter

_ADAPTERS: dict[str, DeviceAdapter] = {
    ShellyPlugGen4Adapter.device_type: ShellyPlugGen4Adapter(),
}


def get_adapter(device_type: str) -> DeviceAdapter:
    adapter = _ADAPTERS.get(device_type)
    if adapter is None:
        raise DeviceConfigurationError(f"unsupported device_type: {device_type}")
    return adapter
