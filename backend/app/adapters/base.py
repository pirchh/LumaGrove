from __future__ import annotations

from typing import Any, Protocol


class DeviceAdapter(Protocol):
    device_type: str

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]: ...

    async def test_connectivity(self, config: dict[str, Any]) -> dict[str, Any]: ...

    async def get_status(self, config: dict[str, Any]) -> dict[str, Any]: ...

    async def set_state(self, config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]: ...
