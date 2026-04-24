# LumaGrove Phase 3/4 overwrite notes

This pack adds the first device onboarding slice for Shelly local LAN control.

## Added

- adapter contract
- Shelly Plug Gen4 adapter
- device request/response schemas
- event log helper
- device state cache helper
- device routes

## Endpoints

- `POST /devices/test-connectivity`
- `POST /devices`
- `GET /devices`
- `GET /devices/{device_id}`

## Example payloads

### Connectivity test

```json
{
  "device_type": "shelly_plug_gen4",
  "config_json": {
    "host": "192.168.1.50",
    "switch_id": 0
  }
}
```

### Create device

```json
{
  "name": "Veg Light Plug",
  "device_type": "shelly_plug_gen4",
  "location_id": null,
  "config_json": {
    "host": "192.168.1.50",
    "switch_id": 0
  },
  "is_enabled": true
}
```

## Install/update dependency

```bat
pip install -r requirements.txt
```

## Run

```bat
python server.py
```
