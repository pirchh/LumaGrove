# LumaGrove Architecture Notes

## Core boundary

The first working vertical slice is:
1. add one Shelly device
2. test connectivity
3. save device
4. turn it on/off manually
5. write an event log entry

## Phase 0 decisions

- Monorepo with `frontend/` and `backend/`
- Backend owns device orchestration and scheduling
- Device identity is internal UUID, never IP address
- Device config is typed JSON per device type
- Public content features stay separate from the control plane until later phases
- Local backend runner is `python server.py`

## Phase 1 backend skeleton

- FastAPI app entrypoint
- settings via environment
- structured logging
- SQLAlchemy session/base
- Alembic scaffold
- `/health` route

## Phase 2 core data model

Start with:
- `locations`
- `devices`
- `event_logs`
- `device_state_cache`

Defer:
- `schedules`
- `overrides`
- `device_groups`

## Why `locations` exists

`locations` is not there to overcomplicate v1.

It is there so physical devices can be grouped by where they actually live:

- room
- tent
- rack
- shelf
- cabinet

That gives you cleaner filtering, better scheduling context later, and easier expansion if the project grows past one test device.

If your real-world setup stays small, `location_id` can remain nullable and mostly ignored until it becomes useful.
