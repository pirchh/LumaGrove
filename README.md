# LumaGrove overwrite pack — Phase 2 core data model

This pack moves the repo from the Phase 1 skeleton into a clean Phase 2 scaffold.

It adds:

- core SQLAlchemy models for `locations`, `devices`, `event_logs`, and `device_state_cache`
- an Alembic migration for those tables
- a small dev seed script
- updated architecture notes

## Apply order

From the repo root, copy these files over your existing project, then run:

```bat
cd backend
alembic upgrade head
python server.py
```

## Why `locations` exists in this pack

`locations` is a lightweight grouping table for physical placement such as:

- grow room
- tent
- rack
- shelf
- lab
- garage

It is optional in v1. A device can exist without a location.

If you want, you can later rename the user-facing language from **Location** to **Zone**, **Area**, or **Space** without changing the core idea much.
