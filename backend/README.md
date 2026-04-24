# LumaGrove Backend — Phase 1 runtime update

This overwrite pack keeps FastAPI + Uvicorn, but changes local startup so you can run the project with:

```bat
python app.py
```

That entrypoint reads your `.env` values through `app.core.config.settings` and feeds them into the Uvicorn runtime.

## What changed

- added `backend/app.py` as the local entrypoint
- added `APP_HOST` and `APP_PORT` support
- kept `DATABASE_URL` as an optional override
- kept compatibility with either `POSTGRES_HOST` or `POSTGRES_SERVER`

## Recommended Windows workflow

```bat
cd C:\Users\ryanj\Development\Websites\LumaGrove\backend
.venv\Scripts\activate
copy .env.example .env
alembic upgrade head
python app.py
```

Then open:

```text
http://127.0.0.1:8003/health
```

## Notes

- `python app.py` still uses Uvicorn under the hood. That is expected and correct for FastAPI.
- If you want a different local port, change `APP_PORT` in `.env`.
- If you already have a full `DATABASE_URL`, you can use that instead of the individual `POSTGRES_*` fields.
