from __future__ import annotations

import asyncio
from contextlib import suppress

from app.core.logging import get_logger
from app.core.time import serialize_utc, utc_now
from app.db.session import SessionLocal
from app.services.schedule_execution import run_scheduler_tick

logger = get_logger(__name__)


async def scheduler_background_loop(
    *,
    stop_event: asyncio.Event,
    interval_seconds: float = 10.0,
    batch_size: int = 25,
) -> None:
    """Run the DB-backed schedule poller inside the FastAPI process.

    The schedules table remains the source of truth. This loop simply wakes up,
    asks the DB for due schedules, executes any that are due, advances their
    next_run_at_utc values, and then sleeps again.
    """
    logger.info(
        "scheduler_background_started",
        interval_seconds=interval_seconds,
        batch_size=batch_size,
    )

    while not stop_event.is_set():
        tick_started_at = utc_now()
        try:
            with SessionLocal() as db:
                tick_result = await run_scheduler_tick(db, batch_size=batch_size)
                if tick_result.due_count:
                    logger.info(
                        "scheduler_background_due_schedules_processed",
                        checked_at_utc=serialize_utc(tick_result.checked_at_utc),
                        due_count=tick_result.due_count,
                    )
                else:
                    logger.info(
                        "scheduler_background_no_due_schedules",
                        checked_at_utc=serialize_utc(tick_result.checked_at_utc),
                    )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception(
                "scheduler_background_tick_failed",
                error=f"{exc.__class__.__name__}: {exc}",
            )

        elapsed_seconds = (utc_now() - tick_started_at).total_seconds()
        sleep_seconds = max(0.0, interval_seconds - elapsed_seconds)

        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(stop_event.wait(), timeout=sleep_seconds)

    logger.info("scheduler_background_stopped")
