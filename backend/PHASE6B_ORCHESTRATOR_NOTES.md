# LumaGrove Phase 6B Orchestrator Pack

This pack adds a console-running scheduler orchestrator.

It is intentionally separate from FastAPI. The API writes schedules into Postgres; the orchestrator sits in the console, polls the schedules table, and executes due work.

## What it does

- polls enabled schedules where `next_run_at_utc <= now()`
- locks due rows with `FOR UPDATE SKIP LOCKED`
- loads the saved device config
- calls the existing device adapter command path
- updates `device_state_cache`
- writes schedule execution event logs
- sets `last_run_at_utc`
- advances `next_run_at_utc`
- keeps running until stopped

## No migration required

This pack uses the schedules table from Phase 6A.

## Run once

Good for testing due schedules without leaving a process running:

```bat
python orchestrator.py --once
```

or:

```bat
python scripts\run_orchestrator.py --once
```

## Run continuously

```bat
python orchestrator.py
```

Custom polling interval:

```bat
python orchestrator.py --interval-seconds 5
```

## Useful test flow

1. Create a schedule due soon using the existing schedule API.
2. Run:

```bat
python orchestrator.py --once
```

3. Check schedule state:

```bat
curl http://127.0.0.1:8003/schedules
```

4. Check logs:

```bat
curl "http://127.0.0.1:8003/event-logs?target_type=schedule&limit=20"
```

## V1 recurrence support

The executor supports the current v1 intent pattern:

- `rrule = FREQ=DAILY`
- `time_local`
- `timezone`

It computes the next UTC run from local wall-clock time + IANA timezone.
