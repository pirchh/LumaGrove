# Phase 7A Auth Notes

This pack adds single-owner admin auth without a users table.

Add these values to `backend/.env`:

```env
ADMIN_USERNAME=charlie
ADMIN_PASSWORD=replace-with-a-long-password
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_EXPIRE_MINUTES=720
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

Public routes:

- `GET /health`
- `POST /auth/login`
- `GET /auth/me` requires token, but is only for checking the logged-in admin session.

Protected routes:

- `/devices/*`
- `/schedules/*`
- `/event-logs/*`

CLI login:

```bat
curl -X POST http://127.0.0.1:8003/auth/login -H "Content-Type: application/json" -d "{\"username\":\"charlie\",\"password\":\"replace-with-a-long-password\"}"
```

Use the token:

```bat
curl http://127.0.0.1:8003/devices -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
