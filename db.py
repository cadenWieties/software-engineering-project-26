# db.py
from typing import Optional
import psycopg2
from config import AppConfig

class PlayerDB:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.conn = psycopg2.connect(
            host=cfg.db_host,
            port=cfg.db_port,
            dbname=cfg.db_name,
            user=cfg.db_user,
            password=cfg.db_password,
        )
        self.conn.autocommit = True
        self._create_table_if_needed()

    def _create_table_if_needed(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    codename VARCHAR(50) NOT NULL
                )
            """)

    def get_codename(self, player_id: int) -> Optional[str]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT codename FROM players WHERE id = %s",
                (player_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None

    def add_player(self, player_id: int, codename: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO players (id, codename)
                VALUES (%s, %s)
                ON CONFLICT (id)
                DO UPDATE SET codename = EXCLUDED.codename
            """, (player_id, codename))

    def close(self) -> None:
        if self.conn:
            self.conn.close()