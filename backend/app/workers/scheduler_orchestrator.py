from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.time import serialize_utc, utc_now
from app.db.session import SessionLocal, check_db_connection
from app.services.schedule_execution import run_scheduler_tick

configure_logging(settings.log_level)
logger = get_logger(__name__)


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return serialize_utc(value)
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def _render_tick_summary(tick_result) -> dict[str, Any]:
    return {
        "checked_at_utc": serialize_utc(tick_result.checked_at_utc),
        "due_count": tick_result.due_count,
        "results": [_jsonable(asdict(result)) for result in tick_result.results],
    }


async def run_orchestrator(*, interval_seconds: float, batch_size: int, once: bool) -> None:
    logger.info(
        "orchestrator_starting",
        environment=settings.environment,
        interval_seconds=interval_seconds,
        batch_size=batch_size,
        once=once,
    )
    check_db_connection()
    logger.info("orchestrator_db_connection_ok")

    while True:
        tick_started_at = utc_now()
        try:
            with SessionLocal() as db:
                tick_result = await run_scheduler_tick(db, batch_size=batch_size)
                summary = _render_tick_summary(tick_result)
                if tick_result.due_count:
                    logger.info("orchestrator_tick_due_schedules_processed", **summary)
                else:
                    logger.info("orchestrator_tick_no_due_schedules", checked_at_utc=summary["checked_at_utc"])
        except Exception as exc:
            logger.exception("orchestrator_tick_failed", error=f"{exc.__class__.__name__}: {exc}")

        if once:
            logger.info("orchestrator_once_complete")
            return

        elapsed_seconds = (utc_now() - tick_started_at).total_seconds()
        sleep_seconds = max(0.0, interval_seconds - elapsed_seconds)
        await asyncio.sleep(sleep_seconds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the LumaGrove schedule orchestrator.")
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=10.0,
        help="Seconds between scheduler polling ticks. Default: 10.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=25,
        help="Maximum due schedules to process per tick. Default: 25.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one scheduler tick and exit.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        asyncio.run(
            run_orchestrator(
                interval_seconds=args.interval_seconds,
                batch_size=args.batch_size,
                once=args.once,
            )
        )
    except KeyboardInterrupt:
        logger.info("orchestrator_stopped_by_user")


if __name__ == "__main__":
    main()
