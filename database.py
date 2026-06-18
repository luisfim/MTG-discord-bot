import sqlite3

DATABASE_FILE = "bot_data.db"


def init_database() -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id INTEGER PRIMARY KEY,
                update_channel_id INTEGER,
                arena_enabled INTEGER NOT NULL DEFAULT 1,
                mtgo_enabled INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        # Handles older database versions that only had guild_id/update_channel_id.
        existing_columns = [
            row[1]
            for row in cursor.execute("PRAGMA table_info(server_settings)").fetchall()
        ]

        if "arena_enabled" not in existing_columns:
            cursor.execute(
                "ALTER TABLE server_settings ADD COLUMN arena_enabled INTEGER NOT NULL DEFAULT 1"
            )

        if "mtgo_enabled" not in existing_columns:
            cursor.execute(
                "ALTER TABLE server_settings ADD COLUMN mtgo_enabled INTEGER NOT NULL DEFAULT 1"
            )

        connection.commit()


def ensure_server_settings(guild_id: int) -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO server_settings (
                guild_id,
                arena_enabled,
                mtgo_enabled
            )
            VALUES (?, 1, 1)
            """,
            (guild_id,),
        )

        connection.commit()


def set_update_channel(guild_id: int, channel_id: int) -> None:
    ensure_server_settings(guild_id)

    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE server_settings
            SET update_channel_id = ?
            WHERE guild_id = ?
            """,
            (channel_id, guild_id),
        )

        connection.commit()


def get_update_channel(guild_id: int) -> int | None:
    ensure_server_settings(guild_id)

    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT update_channel_id
            FROM server_settings
            WHERE guild_id = ?
            """,
            (guild_id,),
        )

        result = cursor.fetchone()

        if result is None:
            return None

        return result[0]


def set_update_sources(guild_id: int, arena_enabled: bool, mtgo_enabled: bool) -> None:
    ensure_server_settings(guild_id)

    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE server_settings
            SET arena_enabled = ?, mtgo_enabled = ?
            WHERE guild_id = ?
            """,
            (int(arena_enabled), int(mtgo_enabled), guild_id),
        )

        connection.commit()


def get_update_settings(guild_id: int) -> dict:
    ensure_server_settings(guild_id)

    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT update_channel_id, arena_enabled, mtgo_enabled
            FROM server_settings
            WHERE guild_id = ?
            """,
            (guild_id,),
        )

        result = cursor.fetchone()

        if result is None:
            return {
                "update_channel_id": None,
                "arena_enabled": True,
                "mtgo_enabled": True,
            }

        return {
            "update_channel_id": result[0],
            "arena_enabled": bool(result[1]),
            "mtgo_enabled": bool(result[2]),
        }