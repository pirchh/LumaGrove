# LumaGrove

LumaGrove is a personal project that combines plant tracking, long-form grow journaling, and lightweight hardware automation into a single system.

At its core, the idea is simple: treat plant growth like a structured timeline instead of scattered notes, and pair that with real-world control over the environment those plants live in.

---

## What it does

LumaGrove is split into two sides:

### Public (Journal / Encyclopedia)

- Card-based homepage for articles and grow logs  
- Timeline-driven article pages with dated sections  
- Structured plant profiles (latin name, origin, preferences, etc.)  
- Categories and tags for organizing content  
- Media-backed entries (images tied to plants, articles, and sections)  

This side is designed to read more like a journal or reference library than a dashboard.

---

### Private (Admin / Control Plane)

- Single-admin authentication system  
- Device control (currently Shelly plugs)  
- Scheduled automation (on/off, time-based execution)  
- Event logging for all actions  
- Admin CMS for:
  - creating plants
  - creating articles
  - attaching plants to articles
  - adding timeline sections
  - uploading media assets  

---

## Architecture

Backend:
- FastAPI
- PostgreSQL
- Alembic migrations
- Local file storage for media
- JWT-based auth (single admin)

Frontend:
- React + Vite + TypeScript
- Tailwind CSS
- API-driven content rendering

---

## Key Concepts

### Timeline-first content
Articles are not just text blobs. They are broken into dated sections, which makes them function more like a log of changes over time.

### Plant + Journal separation
Plant data is structured and reusable. Journal entries reference plants instead of duplicating information.

### Automation underneath
The system is built so that environmental controls (lighting, etc.) live underneath the content layer, not separate from it.

---

## Current State

The project currently supports:

- full backend control plane for devices and schedules  
- public content system (plants, articles, sections)  
- admin CMS for creating and managing content  
- local media upload system with hashing  
- frontend UI for both public and admin views  

---

## Next Steps

- editing flows for content (not just creation)  
- improved taxonomy management (categories/tags UI)  
- theme system  
- optional cloud media storage  
- expanded automation logic  

---

## Notes

This project is intentionally built as a single-user system for now. There is no multi-user auth or permissions model yet.

Everything is designed to be extended later, but kept simple while the core ideas are still evolving.
