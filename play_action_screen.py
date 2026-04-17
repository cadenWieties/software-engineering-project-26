import os
import random
import tkinter as tk
from tkinter import messagebox

try:
    import pygame
except Exception:
    pygame = None

# Sprint 4 Play Action Screen
# Handles countdown, 6-minute timer, scoring logic,
# random music playback, and real-time UI updates
# COLOR THEMES:
BG = "#0a0a0a"
BG_PANEL = "#111111"
GOLD = "#f5c400"
RED_NEON = "#e83030"
GREEN_NEON = "#1fdd60"
DIM = "#aaaaaa"
FG = "#e8e8e8"
FONT = "Courier"

# Sprint 4 requirement: total gameplay duration is 6 minutes
GAME_SECONDS = 6 * 60  # 6 minutes


def make_button(parent, text, cmd, color=GOLD, width=16):
    b = tk.Button(parent, text=text, command=cmd,
                  font=(FONT, 10, "bold"),
                  bg=BG_PANEL, fg=color,
                  activebackground=color, activeforeground=BG,
                  relief="flat", cursor="hand2", width=width,
                  highlightthickness=1, highlightbackground=color)
    b.bind("<Enter>", lambda e: b.config(bg=color, fg=BG))
    b.bind("<Leave>", lambda e: b.config(bg=BG_PANEL, fg=color))
    return b


class PlayActionScreen(tk.Frame):
    def __init__(self, master, red_players, green_players, udp=None, on_back=None):
        super().__init__(master, bg=BG)
        self.on_back = on_back
        self.udp = udp

        self.countdown_value = 30
        self.game_seconds_left = GAME_SECONDS
        self.countdown_running = False
        self.game_running = False
        self.receiver_started = False

        self.red_players = [self.make_player_dict(p) for p in red_players]
        self.green_players = [self.make_player_dict(p) for p in green_players]

        self.base_icon = None
        self.music_ready = False

        self.build_ui()
        self.load_base_icon()
        self.setup_music()
        self.refresh_lists()
        self.update_team_totals()

    def make_player_dict(self, player):
        return {
            "player_id": player.player_id,
            "codename": player.codename,
            "equipment_id": player.equipment_id,
            "score": 0,
            "base_hits": 0
        }

    def build_ui(self):
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top = tk.Frame(self, bg=BG, pady=10)
        top.grid(row=0, column=0, sticky="ew", padx=16)
        top.grid_columnconfigure(1, weight=1)

        tk.Label(top, text="PHOTON", font=(FONT, 22, "bold"),
                 fg=GOLD, bg=BG).grid(row=0, column=0, sticky="w")
        tk.Label(top, text="// PLAY ACTION DISPLAY", font=(FONT, 11),
                 fg=DIM, bg=BG).grid(row=0, column=1, sticky="w", padx=(10, 0))

        make_button(top, "< BACK TO ENTRY", self.go_back,
                    color=DIM, width=18).grid(row=0, column=2, sticky="e")

        tk.Frame(self, bg=GOLD, height=1).grid(row=0, column=0, sticky="ews", padx=16)

        banner = tk.Frame(self, bg=BG_PANEL,
                          highlightthickness=1, highlightbackground=GOLD)
        banner.grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 0))
        banner.grid_columnconfigure(0, weight=1)

        self.timer_label = tk.Label(
            banner,
            text="GAME STARTS IN: 30",
            font=(FONT, 20, "bold"),
            fg=GOLD,
            bg=BG_PANEL,
            pady=10
        )
        self.timer_label.grid(row=0, column=0)

        content = tk.Frame(self, bg=BG)
        content.grid(row=2, column=0, sticky="nsew", padx=16, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=2)
        content.grid_rowconfigure(0, weight=1)

        red_wrap = tk.Frame(content, bg=BG_PANEL,
                            highlightthickness=1, highlightbackground=RED_NEON)
        red_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        red_wrap.grid_rowconfigure(2, weight=1)
        red_wrap.grid_columnconfigure(0, weight=1)

        tk.Label(red_wrap, text="< RED TEAM >", font=(FONT, 11, "bold"),
                 fg=RED_NEON, bg=BG_PANEL).grid(row=0, column=0, pady=(10, 4))

        self.red_total_label = tk.Label(red_wrap, text="TOTAL: 0",
                                        font=(FONT, 10, "bold"),
                                        fg=FG, bg=BG_PANEL)
        self.red_total_label.grid(row=1, column=0, pady=(0, 4))

        self.red_list = tk.Listbox(red_wrap, font=(FONT, 9),
                                   bg=BG_PANEL, fg=RED_NEON,
                                   selectbackground=RED_NEON, selectforeground=BG,
                                   relief="flat", borderwidth=0, highlightthickness=0)
        self.red_list.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 10))

        green_wrap = tk.Frame(content, bg=BG_PANEL,
                              highlightthickness=1, highlightbackground=GREEN_NEON)
        green_wrap.grid(row=0, column=1, sticky="nsew", padx=8)
        green_wrap.grid_rowconfigure(2, weight=1)
        green_wrap.grid_columnconfigure(0, weight=1)

        tk.Label(green_wrap, text="< GREEN TEAM >", font=(FONT, 11, "bold"),
                 fg=GREEN_NEON, bg=BG_PANEL).grid(row=0, column=0, pady=(10, 4))

        self.green_total_label = tk.Label(green_wrap, text="TOTAL: 0",
                                          font=(FONT, 10, "bold"),
                                          fg=FG, bg=BG_PANEL)
        self.green_total_label.grid(row=1, column=0, pady=(0, 4))

        self.green_list = tk.Listbox(green_wrap, font=(FONT, 9),
                                     bg=BG_PANEL, fg=GREEN_NEON,
                                     selectbackground=GREEN_NEON, selectforeground=BG,
                                     relief="flat", borderwidth=0, highlightthickness=0)
        self.green_list.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 10))

        play_wrap = tk.Frame(content, bg=BG_PANEL,
                             highlightthickness=1, highlightbackground=DIM)
        play_wrap.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        play_wrap.grid_rowconfigure(1, weight=1)
        play_wrap.grid_columnconfigure(0, weight=1)

        tk.Label(play_wrap, text="// PLAY BY PLAY", font=(FONT, 11, "bold"),
                 fg=DIM, bg=BG_PANEL).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        self.play_text = tk.Text(play_wrap, font=(FONT, 9), wrap="word",
                                 bg=BG_PANEL, fg=DIM,
                                 insertbackground=GOLD,
                                 relief="flat", borderwidth=0)
        self.play_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        self.play_text.insert("end", "> waiting for game start...\n")
        self.play_text.config(state="disabled")

    def load_base_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "baseicon.jpg")
        if os.path.exists(icon_path):
            try:
                self.base_icon = tk.PhotoImage(file=icon_path)
            except Exception:
                self.base_icon = None

    def setup_music(self):
        if pygame is None:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.music_ready = True
        except Exception:
            self.music_ready = False

    def play_random_music(self):
        if not self.music_ready:
            self.add_play_event("music unavailable")
            return

        music_dir = os.path.join(os.path.dirname(__file__), "assets", "music")
        if not os.path.isdir(music_dir):
            self.add_play_event("music folder not found")
            return

        tracks = []
        for name in os.listdir(music_dir):
            if name.lower().endswith(".mp3"):
                tracks.append(os.path.join(music_dir, name))

        if not tracks:
            self.add_play_event("no mp3 tracks found")
            return

        track = random.choice(tracks)
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.add_play_event(f'playing track: {os.path.basename(track)}')
        except Exception:
            self.add_play_event("could not play music track")

    def stop_music(self):
        if self.music_ready:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def refresh_lists(self):
        self.red_list.delete(0, "end")
        self.green_list.delete(0, "end")

        self.red_players.sort(key=lambda p: p["score"], reverse=True)
        self.green_players.sort(key=lambda p: p["score"], reverse=True)

        for p in self.red_players:
            base_mark = " [BASE]" if p["base_hits"] > 0 else ""
            self.red_list.insert("end", f'{p["codename"]} | {p["score"]} pts{base_mark}')

        for p in self.green_players:
            base_mark = " [BASE]" if p["base_hits"] > 0 else ""
            self.green_list.insert("end", f'{p["codename"]} | {p["score"]} pts{base_mark}')

    def update_team_totals(self):
        red_total = sum(p["score"] for p in self.red_players)
        green_total = sum(p["score"] for p in self.green_players)

        self.red_total_label.config(text=f"TOTAL: {red_total}")
        self.green_total_label.config(text=f"TOTAL: {green_total}")

    def add_play_event(self, text):
        self.play_text.config(state="normal")
        self.play_text.insert("end", f"> {text}\n")
        self.play_text.see("end")
        self.play_text.config(state="disabled")

    def start_countdown(self):
        if not self.countdown_running:
            self.countdown_running = True
            self.tick_countdown()

    def tick_countdown(self):
        val = self.countdown_value

        if val > 10:
            color = GOLD
        elif val > 5:
            color = RED_NEON
        else:
            color = GREEN_NEON

        if val > 0:
            self.timer_label.config(text=f"GAME STARTS IN: {val}", fg=color)
            self.countdown_value -= 1
            self.after(1000, self.tick_countdown)
        else:
            self.timer_label.config(text="GAME IN PROGRESS: 06:00", fg=GREEN_NEON)
            self.add_play_event("game started")
            self.broadcast_code(202)
            self.play_random_music()
            self.start_game_timer()

    def start_game_timer(self):
        self.game_running = True
        self.tick_game_timer()

    def tick_game_timer(self):
        if not self.game_running:
            return

        minutes = self.game_seconds_left // 60
        seconds = self.game_seconds_left % 60
        self.timer_label.config(text=f"GAME IN PROGRESS: {minutes:02d}:{seconds:02d}", fg=GREEN_NEON)

        if self.game_seconds_left > 0:
            self.game_seconds_left -= 1
            self.after(1000, self.tick_game_timer)
        else:
            self.end_game()

    def end_game(self):
        self.game_running = False
        self.timer_label.config(text="GAME OVER", fg=RED_NEON)
        self.add_play_event("game ended")
        self.stop_music()
        self.broadcast_code(221)
        self.broadcast_code(221)
        self.broadcast_code(221)

    def broadcast_code(self, code):
        if self.udp and hasattr(self.udp, "send_equipment_id"):
            try:
                self.udp.send_equipment_id(code)
            except Exception:
                pass

    def find_player_by_equipment(self, equipment_id):
        for p in self.red_players + self.green_players:
            if p["equipment_id"] == equipment_id:
                return p
        return None

    def get_team_name(self, equipment_id):
        for p in self.red_players:
            if p["equipment_id"] == equipment_id:
                return "Red"
        for p in self.green_players:
            if p["equipment_id"] == equipment_id:
                return "Green"
        return None

    def record_hit(self, attacker_equipment_id, target_equipment_id):
        if not self.game_running:
            return

        attacker = self.find_player_by_equipment(attacker_equipment_id)
        target = self.find_player_by_equipment(target_equipment_id)

        if not attacker or not target:
            self.add_play_event(f"unknown hit event: {attacker_equipment_id} -> {target_equipment_id}")
            return

        attacker_team = self.get_team_name(attacker_equipment_id)
        target_team = self.get_team_name(target_equipment_id)

        if attacker_team == target_team:
            attacker["score"] -= 10
            target["score"] -= 10
            self.add_play_event(f'{attacker["codename"]} hit teammate {target["codename"]} (friendly fire)')
            self.broadcast_code(attacker_equipment_id)
            self.broadcast_code(target_equipment_id)
        else:
            attacker["score"] += 10
            self.add_play_event(f'{attacker["codename"]} tagged {target["codename"]} (+10)')
            self.broadcast_code(target_equipment_id)

        self.refresh_lists()
        self.update_team_totals()

    def record_base_hit(self, attacker_equipment_id, base_code):
        if not self.game_running:
            return

        attacker = self.find_player_by_equipment(attacker_equipment_id)
        if not attacker:
            self.add_play_event(f"unknown base hit by hw:{attacker_equipment_id}")
            return

        attacker_team = self.get_team_name(attacker_equipment_id)

        if base_code == 53 and attacker_team == "Green":
            attacker["score"] += 100
            attacker["base_hits"] += 1
            self.add_play_event(f'{attacker["codename"]} scored on red base (+100)')
        elif base_code == 43 and attacker_team == "Red":
            attacker["score"] += 100
            attacker["base_hits"] += 1
            self.add_play_event(f'{attacker["codename"]} scored on green base (+100)')
        else:
            self.add_play_event(f'{attacker["codename"]} triggered base code {base_code}, but no score awarded')

        self.refresh_lists()
        self.update_team_totals()

    def go_back(self):
        if self.game_running:
            if not messagebox.askyesno("Leave Game", "A game is in progress. Go back anyway?"):
                return

        self.stop_music()
        if self.on_back:
            self.on_back()