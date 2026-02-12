# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
from config import AppConfig
from typing import Optional

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
    
    def get_codename(self, player_id: int) -> Optional[str]:
        # Returns codename if player exists, else None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT codename FROM players WHERE player_id = %s", (player_id,))
            row = cur.fetchone()
            return row["codename"] if row else None
        
    
    def add_player(self, player_id: int, codename : str) -> None:
        # Inserts a new player
        # If player_id already exists, this will update codename
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO players (player_id, codename)
                VALUES (%s, %s)
                ON CONFLICT (player_id)
                DO NOT UPDATE SET codename = EXCLUDED.codename
                """,
                (player_id, codename),
            )
    
    def close(self):
        self.conn.close()