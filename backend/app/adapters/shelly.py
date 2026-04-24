from __future__ import annotations

from typing import Any

import httpx

from app.adapters.errors import DeviceConfigurationError, DeviceConnectivityError


class ShellyPlugGen4Adapter:
    device_type = "shelly_plug_gen4"

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(config, dict):
            raise DeviceConfigurationError("config_json must be an object")

        host = config.get("host")
        switch_id = config.get("switch_id", 0)
        username = config.get("username")
        password = config.get("password")

        if not isinstance(host, str) or not host.strip():
            raise DeviceConfigurationError("config_json.host is required")

        if not isinstance(switch_id, int) or switch_id < 0:
            raise DeviceConfigurationError("config_json.switch_id must be a non-negative integer")

        if username is not None and not isinstance(username, str):
            raise DeviceConfigurationError("config_json.username must be a string or null")

        if password is not None and not isinstance(password, str):
            raise DeviceConfigurationError("config_json.password must be a string or null")

        return {
            "host": host.strip(),
            "switch_id": switch_id,
            "username": username or None,
            "password": password or None,
        }

    async def test_connectivity(self, config: dict[str, Any]) -> dict[str, Any]:
        normalized = self.validate_config(config)
        device_info = await self._rpc_call(normalized, "Shelly.GetDeviceInfo")
        status = await self._rpc_call(normalized, "Switch.GetStatus", {"id": normalized["switch_id"]})

        return {
            "reachable": True,
            "host": normalized["host"],
            "device_type": self.device_type,
            "device_info": device_info,
            "switch_status": status,
        }

    async def get_status(self, config: dict[str, Any]) -> dict[str, Any]:
        normalized = self.validate_config(config)
        status = await self._rpc_call(normalized, "Switch.GetStatus", {"id": normalized["switch_id"]})
        return {
            "reachable": True,
            "host": normalized["host"],
            "switch_id": normalized["switch_id"],
            "output": status.get("output"),
            "apower": status.get("apower"),
            "voltage": status.get("voltage"),
            "current": status.get("current"),
            "errors": status.get("errors", []),
            "last_error": None,
            "raw": status,
        }

    async def set_state(self, config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        normalized = self.validate_config(config)
        on = payload.get("on")
        if not isinstance(on, bool):
            raise DeviceConfigurationError("payload.on must be a boolean")

        result = await self._rpc_call(
            normalized,
            "Switch.Set",
            {"id": normalized["switch_id"], "on": on},
        )
        status = await self.get_status(normalized)
        return {
            "command_result": result,
            "status": status,
        }

    async def _rpc_call(
        self,
        config: dict[str, Any],
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"http://{config['host']}/rpc"
        payload: dict[str, Any] = {"id": 1, "method": method}
        if params is not None:
            payload["params"] = params

        auth = None
        if config.get("username") and config.get("password"):
            auth = httpx.DigestAuth(config["username"], config["password"])

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=3.0), auth=auth) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.ConnectTimeout as exc:
            raise DeviceConnectivityError(f"failed to reach Shelly at {config['host']}: connect timeout") from exc
        except httpx.ReadTimeout as exc:
            raise DeviceConnectivityError(f"failed to reach Shelly at {config['host']}: read timeout") from exc
        except httpx.ConnectError as exc:
            raise DeviceConnectivityError(f"failed to reach Shelly at {config['host']}: connection error: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise DeviceConnectivityError(
                f"Shelly at {config['host']} returned HTTP {exc.response.status_code} for {method}"
            ) from exc
        except httpx.HTTPError as exc:
            raise DeviceConnectivityError(
                f"failed to reach Shelly at {config['host']}: {exc.__class__.__name__}: {exc}"
            ) from exc
        except ValueError as exc:
            raise DeviceConnectivityError(f"Shelly at {config['host']} returned non-JSON response: {exc}") from exc

        if "error" in body:
            raise DeviceConnectivityError(f"Shelly RPC error for {method}: {body['error']}")

        result = body.get("result")
        if not isinstance(result, dict):
            raise DeviceConnectivityError(f"unexpected RPC response for {method}")

        return result
