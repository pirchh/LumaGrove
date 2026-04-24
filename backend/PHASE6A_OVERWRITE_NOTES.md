# LumaGrove Phase 6A Overwrite Notes

This pack adds the schedule schema scaffold and schedule CRUD API.

## What changed

- Added `Schedule` SQLAlchemy model.
- Added Alembic migration `0003_phase6a_schedules.py`.
- Added schedule schemas.
- Added schedule time helper for local wall-clock intent -> UTC next run calculation.
- Added schedule routes:
  - `POST /devices/{device_id}/schedules`
  - `GET /devices/{device_id}/schedules`
  - `GET /schedules`
  - `GET /schedules/{schedule_id}`
  - `PATCH /schedules/{schedule_id}`
  - `DELETE /schedules/{schedule_id}`
- Registered the schedules router in `app/main.py`.

## Current schedule rule

For v1, recurring schedules store:

- local wall-clock time, for example `07:00`
- IANA timezone, for example `America/New_York`
- recurrence rule, currently only `FREQ=DAILY`
- computed `next_run_at_utc`

The worker/execution loop is not included in this pack. That is Phase 6B.
