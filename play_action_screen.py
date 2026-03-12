# play_action_screen.py
import tkinter as tk

# COLOR THEMES:
BG = "#0a0a0a"
BG_PANEL = "#111111"
GOLD = "#f5c400"
RED_NEON = "#e83030"
GREEN_NEON = "#1fdd60"
DIM = "#aaaaaa"
FG = "#e8e8e8"
FONT = "Courier"

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
    def __init__(self, master, red_players, green_players, on_back=None):
        super().__init__(master, bg=BG)
        self.red_players = red_players
        self.green_players = green_players
        self.on_back = on_back
        self.countdown_value = 30
        self.countdown_running = False

        self.build_ui()
        self.load_players()

    def build_ui(self):
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # top bar
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

        # countdown banner
        banner = tk.Frame(self, bg=BG_PANEL,
                          highlightthickness=1, highlightbackground=GOLD)
        banner.grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 0))
        banner.grid_columnconfigure(0, weight=1)

        self.countdown_label = tk.Label(banner, text="GAME STARTS IN:  30",
                                        font=(FONT, 20, "bold"),
                                        fg=GOLD, bg=BG_PANEL, pady=10)
        self.countdown_label.grid(row=0, column=0)

        # main content area
        content = tk.Frame(self, bg=BG)
        content.grid(row=2, column=0, sticky="nsew", padx=16, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # red team box
        red_wrap = tk.Frame(content, bg=BG_PANEL,
                            highlightthickness=1, highlightbackground=RED_NEON)
        red_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        red_wrap.grid_rowconfigure(1, weight=1)
        red_wrap.grid_columnconfigure(0, weight=1)

        tk.Label(red_wrap, text="< RED TEAM >", font=(FONT, 11, "bold"),
                 fg=RED_NEON, bg=BG_PANEL).grid(row=0, column=0, pady=(10, 6))
        self.red_list = tk.Listbox(red_wrap, font=(FONT, 9),
                                   bg=BG_PANEL, fg=RED_NEON,
                                   selectbackground=RED_NEON, selectforeground=BG,
                                   relief="flat", borderwidth=0, highlightthickness=0)
        self.red_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 10))

        # green team box
        green_wrap = tk.Frame(content, bg=BG_PANEL,
                              highlightthickness=1, highlightbackground=GREEN_NEON)
        green_wrap.grid(row=0, column=1, sticky="nsew", padx=8)
        green_wrap.grid_rowconfigure(1, weight=1)
        green_wrap.grid_columnconfigure(0, weight=1)

        tk.Label(green_wrap, text="< GREEN TEAM >", font=(FONT, 11, "bold"),
                 fg=GREEN_NEON, bg=BG_PANEL).grid(row=0, column=0, pady=(10, 6))
        self.green_list = tk.Listbox(green_wrap, font=(FONT, 9),
                                     bg=BG_PANEL, fg=GREEN_NEON,
                                     selectbackground=GREEN_NEON, selectforeground=BG,
                                     relief="flat", borderwidth=0, highlightthickness=0)
        self.green_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 10))

        # play by play
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
                                 relief="flat", borderwidth=0, state="normal")
        self.play_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        self.play_text.insert("end", "> game events will appear here.\n")
        self.play_text.insert("end", "> sprint 3 is display only, no live events yet.\n")
        self.play_text.config(state="disabled")

    def load_players(self):
        self.red_list.delete(0, "end")
        self.green_list.delete(0, "end")
        for p in self.red_players:
            self.red_list.insert("end", f" {p.codename}  (id:{p.player_id}, hw:{p.equipment_id})")
        for p in self.green_players:
            self.green_list.insert("end", f" {p.codename}  (id:{p.player_id}, hw:{p.equipment_id})")

    def start_countdown(self):
        if not self.countdown_running:
            self.countdown_running = True
            self.tick()

    def tick(self):
        val = self.countdown_value
        if val > 10:
            color = GOLD
        elif val > 5:
            color = RED_NEON
        else:
            color = GREEN_NEON

        if val > 0:
            self.countdown_label.config(text=f"GAME STARTS IN:  {val}", fg=color)
            self.countdown_value -= 1
            self.after(1000, self.tick)
        else:
            self.countdown_label.config(text="> GAME STARTED <", fg=GREEN_NEON)

    def go_back(self):
        if self.on_back:
            self.on_back()