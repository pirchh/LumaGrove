# LumaGrove Phase 5 Overwrite Pack

This pack moves the project into the manual-control slice.

## What changed

- Added `GET /devices/{device_id}/status`
- Added `POST /devices/{device_id}/commands/power`
- Improved device creation to try an initial live status fetch and hydrate `device_state_cache`
- Improved Shelly connectivity errors so the exception type is included
- Added a small helper for unreachable state cache payloads

## No migration required

This pack is app-layer only.

## Suggested CLI checks

Health:

```bat
curl http://127.0.0.1:8003/health
```

Refresh live status:

```bat
curl http://127.0.0.1:8003/devices/YOUR-DEVICE-UUID/status
```

Turn off:

```bat
curl -X POST http://127.0.0.1:8003/devices/YOUR-DEVICE-UUID/commands/power -H "Content-Type: application/json" -d "{\"on\":false}"
```

Turn on:

```bat
curl -X POST http://127.0.0.1:8003/devices/YOUR-DEVICE-UUID/commands/power -H "Content-Type: application/json" -d "{\"on\":true}"
```

List devices:

```bat
curl http://127.0.0.1:8003/devices
```
