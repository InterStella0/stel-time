from dataclasses import dataclass

import os

import asqlite
from pathlib import Path

DB_PATH = Path(os.environ.get("DB_PATH", "data.db"))


@dataclass
class UserTimezone:
    user_id: int
    timezone: str | None
    offset: float | None


class Database:
    def __init__(self):
        self.pool: asqlite.Pool | None = None

    async def setup(self) -> None:
        self.pool = await asqlite.create_pool(DB_PATH)
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_timezones (
                    user_id  INTEGER PRIMARY KEY,
                    timezone TEXT,
                    offset   REAL
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bot_meta (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    async def get_synced_version(self) -> str | None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            row = await conn.fetchone("SELECT value FROM bot_meta WHERE key = 'version'")
            return row["value"] if row else None

    async def set_synced_version(self, version: str) -> None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO bot_meta (key, value) VALUES ('version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (version,))

    async def set_timezone(self, user_id: int, timezone: str) -> None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_timezones (user_id, timezone, offset)
                VALUES (?, ?, NULL)
                ON CONFLICT(user_id) DO UPDATE SET timezone = excluded.timezone, offset = NULL
            """, (user_id, timezone))

    async def set_offset(self, user_id: int, offset: float) -> None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_timezones (user_id, timezone, offset)
                VALUES (?, NULL, ?)
                ON CONFLICT(user_id) DO UPDATE SET timezone = NULL, offset = excluded.offset
            """, (user_id, offset))

    async def fetch_user(self, user_id: int) -> UserTimezone | None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            row = await conn.fetchone(
                "SELECT * FROM user_timezones WHERE user_id = ?", (user_id,)
            )
            if row is None:
                return None
            return UserTimezone(user_id=row["user_id"], timezone=row["timezone"], offset=row["offset"])

    async def delete_user(self, user_id: int) -> None:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM user_timezones WHERE user_id = ?", (user_id,)
            )
