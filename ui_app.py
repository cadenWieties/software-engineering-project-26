# ui_app.py
import os
import tkinter as tk
from tkinter import ttk

from splash import SplashScreen
from entry_screen import PlayerEntryScreen
from play_action_screen import PlayActionScreen

from config import AppConfig
from db import PlayerDB
from udp_comm import UDPComm

class MockDB:
    def __init__(self):
        self.data = {}

    def get_codename(self, player_id: int):
        return self.data.get(player_id)

    def add_player(self, player_id: int, codename: str):
        self.data[player_id] = codename
        print(f"[MOCK DB] added {player_id} -> {codename}")

    def close(self):
        pass

class MockUDP:
    def __init__(self):
        self.target_ip = "127.0.0.1"

    def set_target_ip(self, ip: str):
        self.target_ip = ip
        print(f"[MOCK UDP] target ip set to {ip}")

    def send_equipment_id(self, equipment_id: int):
        print(f"[MOCK UDP] sent equipment id {equipment_id} to {self.target_ip}:7500")

    def close(self):
        pass

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(ASSETS_DIR, "logo.jpg")

def center_window(win, w=1100, h=650):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")



def main():
    root = tk.Tk()
    root.title("Photon - Sprint 3 UI")

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.withdraw()

    cfg = AppConfig()

    # fallback for: real services first, mock if unavailable
    try:
        db = PlayerDB(cfg)
        print("[INFO] Connected to real PostgreSQL database.")
    except Exception as e:
        print(f"[WARNING] Could not connect to PostgreSQL. Using MockDB instead.\n{e}")
        db = MockDB()

    try:
        udp = UDPComm(cfg)
        print("[INFO] UDP initialized.")
    except Exception as e:
        print(f"[WARNING] Could not initialize UDP. Using MockUDP instead.\n{e}")
        udp = MockUDP()

    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)

    def clear_container():
        for widget in container.winfo_children():
            widget.destroy()

    def show_entry():
        clear_container()
        center_window(root, 900, 520)

        screen = PlayerEntryScreen(
            container,
            db=db,
            udp=udp,
            on_start_game=show_play_action
        )
        screen.pack(fill="both", expand=True)

    def show_play_action(red_players, green_players):
        clear_container()
        center_window(root, 1100, 650)

        screen = PlayActionScreen(
            container,
            red_players=red_players,
            green_players=green_players,
            on_back=show_entry
        )
        screen.pack(fill="both", expand=True)
        screen.start_countdown()

    def on_close():
        try:
            db.close()
        except Exception:
            pass
        try:
            udp.close()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    def after_splash():
        root.deiconify()
        show_entry()

    root._splash = SplashScreen(root, LOGO_PATH, on_done=after_splash, ms=3000)
    root.mainloop()

if __name__ == "__main__":
    main()