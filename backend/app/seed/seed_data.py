import asyncio
import random
from datetime import datetime, timedelta

from app.config import settings
from app.db.sqlite.connection import init_db
from app.db.factory import get_repositories
from app.auth.password import hash_password

DEMO_USERS = [
    {"username": "user", "password": "pass123", "role": "user", "location": "Manila"},
    {"username": "admin", "password": "admin123", "role": "admin", "location": "Quezon City"},
    {"username": "maria", "password": "pass123", "role": "user", "location": "Cebu City"},
    {"username": "juan", "password": "pass123", "role": "user", "location": "Davao City"},
    {"username": "ana", "password": "pass123", "role": "user", "location": "Makati"},
    {"username": "carlos", "password": "pass123", "role": "user", "location": "Quezon City"},
    {"username": "sofia", "password": "pass123", "role": "user", "location": "Manila"},
    {"username": "miguel", "password": "pass123", "role": "user", "location": "Cebu City"},
    {"username": "liza", "password": "pass123", "role": "user", "location": "Davao City"},
    {"username": "rico", "password": "pass123", "role": "user", "location": "Makati"},
]

STATUSES = ["good", "good", "good", "good", "good", "good", "warning", "warning", "warning", "poor", "poor"]


def random_angle(status: str) -> float:
    if status == "good":
        return round(random.uniform(0, 10), 2)
    elif status == "warning":
        return round(random.uniform(10, 20), 2)
    else:
        return round(random.uniform(20, 45), 2)


async def seed():
    print("Initializing database...")
    await init_db(settings.db_path)
    repos = get_repositories()

    print("Creating demo users...")
    for u in DEMO_USERS:
        existing = await repos.users.get_by_username(u["username"])
        if existing:
            print(f"  User '{u['username']}' already exists, skipping.")
            continue
        await repos.users.create(
            username=u["username"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
            location=u["location"],
        )
        print(f"  Created user '{u['username']}' ({u['role']}) — {u['location']}")

    print("Generating posture records and sessions...")
    all_users = await repos.users.list_all()
    for user in all_users:
        if user.role == "admin":
            continue

        days = 21
        records_per_day = 8

        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            session_id = await repos.sessions.start_session(user.id)

            good_count = 0
            warning_count = 0
            poor_count = 0
            angles = []

            for i in range(records_per_day):
                timestamp = date - timedelta(hours=day * 24 // days, minutes=i * 30)
                status = random.choice(STATUSES)
                angle = random_angle(status)
                duration = round(random.uniform(2.0, 15.0), 2)

                await repos.posture.insert(
                    user_id=user.id,
                    status=status,
                    angle=angle,
                    duration=duration,
                    session_id=session_id,
                )

                angles.append(angle)
                if status == "good":
                    good_count += 1
                elif status == "warning":
                    warning_count += 1
                else:
                    poor_count += 1

            avg_angle = round(sum(angles) / len(angles), 2) if angles else None
            await repos.sessions.end_session(
                session_id=session_id,
                good_count=good_count,
                warning_count=warning_count,
                poor_count=poor_count,
                avg_angle=avg_angle,
            )

        print(f"  Generated {days * records_per_day} records for '{user.username}'")

    print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
