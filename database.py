import sqlite3

DATABASE_FILE = "bot_data.db"


def init_database() -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id INTEGER PRIMARY KEY,
                update_channel_id INTEGER NOT NULL
            )
            """
        )

        connection.commit()


def set_update_channel(guild_id: int, channel_id: int) -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO server_settings (guild_id, update_channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
            DO UPDATE SET update_channel_id = excluded.update_channel_id
            """,
            (guild_id, channel_id),
        )

        connection.commit()


def get_update_channel(guild_id: int) -> int | None:
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