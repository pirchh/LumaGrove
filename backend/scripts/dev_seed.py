from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Device, DeviceStateCache, EventLog, Location
from app.db.session import SessionLocal


def seed(db: Session) -> None:
    location = db.query(Location).filter(Location.slug == "main-grow-room").one_or_none()
    if location is None:
        location = Location(
            name="Main Grow Room",
            slug="main-grow-room",
            description="Default dev location for first hardware tests.",
        )
        db.add(location)
        db.flush()

    device = db.query(Device).filter(Device.name == "Shelly Test Plug").one_or_none()
    if device is None:
        device = Device(
            name="Shelly Test Plug",
            device_type="shelly_plug_gen4",
            location_id=location.id,
            config_json={
                "ip_address": "192.168.1.50",
                "switch_id": 0,
            },
            is_enabled=True,
        )
        db.add(device)
        db.flush()

    if device.state_cache is None:
        db.add(
            DeviceStateCache(
                device_id=device.id,
                status_json={
                    "reachable": False,
                    "power": "unknown",
                },
            )
        )

    db.add(
        EventLog(
            event_type="seeded_device",
            target_type="device",
            target_id=device.id,
            severity="info",
            message="Seeded first development device.",
            payload_json={"device_name": device.name},
        )
    )

    db.commit()


if __name__ == "__main__":
    with SessionLocal() as db:
        seed(db)
        print("Seed complete.")
