import sqlite3
import logging

logger = logging.getLogger(__name__)


class Database:

    # ===================== INIT =====================

    def __init__(self, db_path: str = "movies.db"):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # ===================== TABLES =====================

    def _create_tables(self):

        with self._connect() as conn:

            # ================= MOVIES =================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    file_id TEXT NOT NULL,
                    file_type TEXT NOT NULL DEFAULT 'video',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ================= CHANNELS =================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT UNIQUE,
                    channel_name TEXT
                )
            """)

            conn.commit()

        logger.info("Database tayyor.")

    # ===================== MOVIES =====================

    def add_movie(
        self,
        code: str,
        name: str,
        description: str,
        file_id: str,
        file_type: str
    ) -> bool:

        try:

            with self._connect() as conn:

                conn.execute(
                    """
                    INSERT INTO movies
                    (code, name, description, file_id, file_type)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        code,
                        name,
                        description,
                        file_id,
                        file_type
                    )
                )

                conn.commit()

            return True

        except sqlite3.IntegrityError:

            logger.warning(
                f"Kod allaqachon mavjud: {code}"
            )

            return False

        except Exception as e:

            logger.error(
                f"add_movie xato: {e}"
            )

            return False

    def get_movie_by_code(self, code: str):

        try:

            with self._connect() as conn:

                cursor = conn.execute(
                    """
                    SELECT
                        id,
                        code,
                        name,
                        description,
                        file_id,
                        file_type
                    FROM movies
                    WHERE code = ?
                    """,
                    (code,)
                )

                return cursor.fetchone()

        except Exception as e:

            logger.error(
                f"get_movie_by_code xato: {e}"
            )

            return None

    def get_all_movies(self):

        try:

            with self._connect() as conn:

                cursor = conn.execute(
                    """
                    SELECT
                        id,
                        code,
                        name,
                        description,
                        file_id,
                        file_type
                    FROM movies
                    ORDER BY created_at DESC
                    """
                )

                return cursor.fetchall()

        except Exception as e:

            logger.error(
                f"get_all_movies xato: {e}"
            )

            return []

    def delete_movie_by_code(self, code: str) -> bool:

        try:

            with self._connect() as conn:

                conn.execute(
                    "DELETE FROM movies WHERE code = ?",
                    (code,)
                )

                conn.commit()

            return True

        except Exception as e:

            logger.error(
                f"delete_movie_by_code xato: {e}"
            )

            return False

    def get_movie_count(self) -> int:

        try:

            with self._connect() as conn:

                cursor = conn.execute(
                    "SELECT COUNT(*) FROM movies"
                )

                return cursor.fetchone()[0]

        except Exception as e:

            logger.error(
                f"get_movie_count xato: {e}"
            )

            return 0

    # ===================== CHANNELS =====================

    def add_channel(
        self,
        channel_id,
        channel_name
    ):

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO channels
            (channel_id, channel_name)
            VALUES (?, ?)
            """,
            (
                channel_id,
                channel_name
            )
        )

        conn.commit()
        conn.close()

    def get_channels(self):

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM channels"
        )

        channels = cursor.fetchall()

        conn.close()

        return channels

    def delete_channel(self, channel_id):

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM channels
            WHERE channel_id = ?
            """,
            (channel_id,)
        )

        conn.commit()
        conn.close()