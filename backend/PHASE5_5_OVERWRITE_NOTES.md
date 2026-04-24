# LumaGrove Phase 5.5 overwrite notes

This pack is a hardening pass before scheduling work.

## What changed

- UTC serialization cleanup for `*_utc` API fields
  - responses now normalize those datetimes to UTC and serialize with `Z`
- added event log read endpoints
  - `GET /event-logs`
  - `GET /devices/{device_id}/event-logs`
- improved unreachable state cache payloads
  - now includes `errors` plus `last_error`
- improved Shelly adapter error messages
  - connect timeout
  - read timeout
  - connection error
  - HTTP status error
  - malformed JSON / RPC response
- stricter Shelly config validation for username/password types

## No migration required

This is app-layer hardening only.

## Useful curls

### Global recent event logs

```bat
curl "http://127.0.0.1:8003/event-logs"
```

### Per-device recent event logs

```bat
curl "http://127.0.0.1:8003/devices/PUT-DEVICE-UUID-HERE/event-logs"
```

### Event logs with explicit limit

```bat
curl "http://127.0.0.1:8003/event-logs?limit=20"
```

### Device logs with explicit limit

```bat
curl "http://127.0.0.1:8003/devices/PUT-DEVICE-UUID-HERE/event-logs?limit=20"
```
