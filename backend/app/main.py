from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.dependencies import require_admin
from app.api.routes.admin_assets import router as admin_assets_router
from app.api.routes.admin_content import router as admin_content_router
from app.api.routes.auth import router as auth_router
from app.api.routes.devices import router as devices_router
from app.api.routes.event_logs import router as event_logs_router
from app.api.routes.health import router as health_router
from app.api.routes.public_content import router as public_content_router
from app.api.routes.schedules import router as schedules_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import check_db_connection
from app.workers.scheduler_background import scheduler_background_loop

configure_logging(settings.log_level)
logger = get_logger(__name__)

SCHEDULER_INTERVAL_SECONDS = 10.0
SCHEDULER_BATCH_SIZE = 25
MEDIA_ROOT = Path(__file__).resolve().parents[1] / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
(MEDIA_ROOT / "uploads").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", environment=settings.environment)

    scheduler_stop_event: asyncio.Event | None = None
    scheduler_task: asyncio.Task | None = None

    try:
        check_db_connection()
        logger.info("db_connection_ok")
    except Exception as exc:
        logger.warning("db_connection_failed", error=str(exc))
    else:
        scheduler_stop_event = asyncio.Event()
        scheduler_task = asyncio.create_task(
            scheduler_background_loop(
                stop_event=scheduler_stop_event,
                interval_seconds=SCHEDULER_INTERVAL_SECONDS,
                batch_size=SCHEDULER_BATCH_SIZE,
            )
        )
        app.state.scheduler_stop_event = scheduler_stop_event
        app.state.scheduler_task = scheduler_task
        logger.info(
            "scheduler_background_task_created",
            interval_seconds=SCHEDULER_INTERVAL_SECONDS,
            batch_size=SCHEDULER_BATCH_SIZE,
        )

    try:
        yield
    finally:
        logger.info("app_stopping")
        if scheduler_stop_event is not None:
            scheduler_stop_event.set()
        if scheduler_task is not None:
            scheduler_task.cancel()
            with suppress(asyncio.CancelledError):
                await scheduler_task
        logger.info("app_stopped")


app = FastAPI(
    title="LumaGrove API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(public_content_router)

# Admin/control-plane APIs are protected by the single-owner auth layer.
app.include_router(devices_router, dependencies=[Depends(require_admin)])
app.include_router(event_logs_router, dependencies=[Depends(require_admin)])
app.include_router(schedules_router, dependencies=[Depends(require_admin)])
app.include_router(admin_content_router, dependencies=[Depends(require_admin)])
app.include_router(admin_assets_router, dependencies=[Depends(require_admin)])
