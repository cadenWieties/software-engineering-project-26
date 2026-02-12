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
            cur.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
            row = cur.fetchone()
            return row["codename"] if row else None
        
    
    def add_player(self, player_id: int, codename : str) -> None:
        # Inserts a new player
        # If player_id already exists, this will update codename
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE players SET codename = %s WHERE id = %s",
                (codename, player_id),
            )
            
            # If no row updated, insert new
            if cur.rowCount == 0:
                cur.execute(
                    "INSERT INTO players (id, codename) VALUES (%s, %s)",
                    (player_id, codename),
                )
    
    def close(self):
        self.conn.close()