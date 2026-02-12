# ui_app.py
import os
import tkinter as tk
from tkinter import ttk, messagebox

from splash import SplashScreen
from entry_screen import PlayerEntryScreen


# isolated laptop testing

class MockDB:
    def __init__(self):
        self.data = {}

    def get_codename(self, player_id: int):
        return self.data.get(player_id)

    def add_player(self, player_id: int, codename: str):
        self.data[player_id] = codename
        print(f"[MOCK DB] {player_id} -> {codename}")


class MockUDP:
    def __init__(self):
        self.target_ip = "127.0.0.1"

    def set_target_ip(self, ip: str):
        self.target_ip = ip
        print(f"[MOCK UDP] target ip = {ip}")

    def send_equipment_id(self, equipment_id: int):
        print(f"[MOCK UDP] send equipment {equipment_id} to {self.target_ip}:7500")


# app  run
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(ASSETS_DIR, "logo.jpg")


def center_window(win, w=900, h=520):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


def main():
    root = tk.Tk()
    root.title("Photon - Sprint 2 UI")

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Hide main window during splash
    root.withdraw()

    # Create services
    db = MockDB()
    udp = MockUDP()

    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)

    def on_start_game(red_players, green_players):
        messagebox.showinfo(
            "Start (Sprint 2 Stub)",
            f"Red players: {len(red_players)}\nGreen players: {len(green_players)}"
        )

    def show_entry():
        root.deiconify()
        center_window(root, 900, 520)

        for w in container.winfo_children():
            w.destroy()

        screen = PlayerEntryScreen(container, db=db, udp=udp, on_start_game=on_start_game)
        screen.pack(fill="both", expand=True)

    root._splash = SplashScreen(root, LOGO_PATH, on_done=show_entry, ms=3000)

    root.mainloop()


if __name__ == "__main__":
    main()