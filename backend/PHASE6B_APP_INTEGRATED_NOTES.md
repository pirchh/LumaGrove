# Phase 6B — App-Integrated Scheduler Orchestrator

This pack keeps the schedules table as the source of truth, but starts the scheduler poller from FastAPI lifespan.

## Runtime

Run the whole control plane with:

```bat
python server.py
```

That now starts:

- FastAPI routes
- DB connection check
- background scheduler poller

The scheduler wakes every 10 seconds, finds enabled schedules whose `next_run_at_utc <= now`, executes them, updates device state cache, writes event logs, and advances `next_run_at_utc`.

## Optional CLI runner

The standalone runner is still included for one-off debugging:

```bat
python orchestrator.py --once
```

or:

```bat
python orchestrator.py --interval-seconds 5
```

## No migration

No new migration is required if Phase 6A is already applied.
