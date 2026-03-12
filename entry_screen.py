# entry_screen.py
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass

# COLOR THEMES:
BG = "#0a0a0a"
BG_PANEL = "#111111"
BG_INPUT = "#1a1a1a"
GOLD = "#f5c400"
RED_NEON = "#e83030"
GREEN_NEON = "#1fdd60"
DIM = "#aaaaaa"
FG = "#e8e8e8"
FONT = "Courier"

MAX_PER_TEAM = 15

@dataclass
class PlayerRow:
    player_id: int
    codename: str
    equipment_id: int

# helper to make a styled button
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

def make_entry(parent, var, width=18):
    return tk.Entry(parent, textvariable=var, width=width,
                    font=(FONT, 10), bg=BG_INPUT, fg=FG,
                    insertbackground=GOLD, relief="flat",
                    highlightthickness=1,
                    highlightbackground=DIM, highlightcolor=GOLD)

class PlayerEntryScreen(tk.Frame):
    def __init__(self, master, db, udp, on_start_game):
        super().__init__(master, bg=BG)
        self.db = db
        self.udp = udp
        self.on_start_game = on_start_game
        self.red_team = []
        self.green_team = []

        self.build_ui()
        self.bind_keys()
        self.refresh_lists()

    def build_ui(self):
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # top bar
        top = tk.Frame(self, bg=BG, pady=10)
        top.grid(row=0, column=0, sticky="ew", padx=16)
        top.grid_columnconfigure(1, weight=1)

        tk.Label(top, text="PHOTON", font=(FONT, 22, "bold"),
                 fg=GOLD, bg=BG).grid(row=0, column=0, sticky="w")
        tk.Label(top, text="// PLAYER ENTRY", font=(FONT, 11),
                 fg=DIM, bg=BG).grid(row=0, column=1, sticky="w", padx=(10, 0))

        # udp ip field in the top bar
        net = tk.Frame(top, bg=BG)
        net.grid(row=0, column=2, sticky="e")
        tk.Label(net, text="UDP TARGET:", font=(FONT, 9),
                 fg=DIM, bg=BG).pack(side="left", padx=(0, 4))
        self.ip_var = tk.StringVar(value=getattr(self.udp, "target_ip", "127.0.0.1"))
        tk.Entry(net, textvariable=self.ip_var, width=15,
                 font=(FONT, 10), bg=BG_INPUT, fg=GOLD,
                 insertbackground=GOLD, relief="flat",
                 highlightthickness=1, highlightbackground=DIM,
                 highlightcolor=GOLD).pack(side="left", padx=(0, 6))
        make_button(net, "SET", self.set_ip, color=GOLD, width=5).pack(side="left")

        tk.Frame(self, bg=GOLD, height=1).grid(row=0, column=0, sticky="ews", padx=16)

        # main area
        content = tk.Frame(self, bg=BG)
        content.grid(row=1, column=0, sticky="nsew", padx=16, pady=10)
        content.grid_columnconfigure(0, weight=0)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.build_form(content)
        self.build_rosters(content)

        # bottom bar
        bottom = tk.Frame(self, bg=BG, pady=10)
        bottom.grid(row=2, column=0, sticky="ew", padx=16)
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        tk.Label(bottom, text="[F12] CLEAR ALL  |  [F5] START GAME  |  [ENTER] ADD PLAYER",
                 font=(FONT, 9), fg=DIM, bg=BG).grid(row=0, column=0, sticky="w")

        btns = tk.Frame(bottom, bg=BG)
        btns.grid(row=0, column=1, sticky="e")
        make_button(btns, "[ F12 ] CLEAR ALL", self.clear_all, color=DIM, width=20).pack(side="left", padx=(0, 8))
        make_button(btns, "[ F5 ] START  >", self.start, color=GREEN_NEON, width=20).pack(side="left")

    def build_form(self, parent):
        form = tk.Frame(parent, bg=BG_PANEL, padx=14, pady=12,
                        highlightthickness=1, highlightbackground=DIM)
        form.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        # section header
        hdr = tk.Frame(form, bg=BG_PANEL)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text="[ ADD PLAYER ]", font=(FONT, 9, "bold"),
                 fg=GOLD, bg=BG_PANEL).pack(side="left")
        tk.Frame(hdr, bg=GOLD, height=1).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # team selector
        row = tk.Frame(form, bg=BG_PANEL)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="TEAM", font=(FONT, 10), fg=DIM, bg=BG_PANEL).pack(side="left", padx=(0, 8))
        self.team_var = tk.StringVar(value="Red")
        m = tk.OptionMenu(row, self.team_var, "Red", "Green")
        m.config(font=(FONT, 10), bg=BG_INPUT, fg=GOLD,
                 activebackground=GOLD, activeforeground=BG,
                 highlightthickness=0, relief="flat", width=8)
        m["menu"].config(bg=BG_INPUT, fg=FG, font=(FONT, 10))
        m.pack(side="left")

        # player id
        row2 = tk.Frame(form, bg=BG_PANEL)
        row2.pack(fill="x", pady=4)
        tk.Label(row2, text="PLAYER ID", font=(FONT, 10), fg=DIM, bg=BG_PANEL).pack(side="left", padx=(0, 8))
        self.player_id_var = tk.StringVar()
        make_entry(row2, self.player_id_var, width=12).pack(side="left", padx=(0, 6))
        make_button(row2, "LOOKUP", self.lookup, color=DIM, width=8).pack(side="left")

        # codename
        row3 = tk.Frame(form, bg=BG_PANEL)
        row3.pack(fill="x", pady=4)
        tk.Label(row3, text="CODENAME ", font=(FONT, 10), fg=DIM, bg=BG_PANEL).pack(side="left", padx=(0, 8))
        self.codename_var = tk.StringVar()
        make_entry(row3, self.codename_var, width=20).pack(side="left")

        # hardware id
        row4 = tk.Frame(form, bg=BG_PANEL)
        row4.pack(fill="x", pady=4)
        tk.Label(row4, text="HARDWARE  ", font=(FONT, 10), fg=DIM, bg=BG_PANEL).pack(side="left", padx=(0, 8))
        self.equipment_id_var = tk.StringVar()
        make_entry(row4, self.equipment_id_var, width=20).pack(side="left")

        tk.Frame(form, bg=DIM, height=1).pack(fill="x", pady=12)

        make_button(form, "[ ENTER ]  ADD PLAYER", self.add_player,
                    color=GOLD, width=24).pack(fill="x")

        tk.Label(form, text="auto-fills codename from DB if found",
                 font=(FONT, 8), fg=DIM, bg=BG_PANEL).pack(pady=(6, 0))

    def build_rosters(self, parent):
        roster = tk.Frame(parent, bg=BG)
        roster.grid(row=0, column=1, sticky="nsew")
        roster.grid_columnconfigure(0, weight=1)
        roster.grid_columnconfigure(1, weight=1)
        roster.grid_rowconfigure(1, weight=1)

        # rosters header
        hdr = tk.Frame(roster, bg=BG)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        tk.Label(hdr, text=f"[ ROSTERS  (max {MAX_PER_TEAM} per team) ]",
                 font=(FONT, 9, "bold"), fg=GOLD, bg=BG).pack(side="left")
        tk.Frame(hdr, bg=GOLD, height=1).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # red panel
        red_wrap = tk.Frame(roster, bg=BG_PANEL,
                            highlightthickness=1, highlightbackground=RED_NEON)
        red_wrap.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        red_wrap.grid_rowconfigure(1, weight=1)
        red_wrap.grid_columnconfigure(0, weight=1)

        tk.Label(red_wrap, text="< RED TEAM >", font=(FONT, 10, "bold"),
                 fg=RED_NEON, bg=BG_PANEL).grid(row=0, column=0, pady=(8, 4))
        self.red_list = tk.Listbox(red_wrap, font=(FONT, 9),
                                   bg=BG_PANEL, fg=RED_NEON,
                                   selectbackground=RED_NEON, selectforeground=BG,
                                   relief="flat", borderwidth=0, highlightthickness=0)
        self.red_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # green panel
        green_wrap = tk.Frame(roster, bg=BG_PANEL,
                              highlightthickness=1, highlightbackground=GREEN_NEON)
        green_wrap.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        green_wrap.grid_rowconfigure(1, weight=1)
        green_wrap.grid_columnconfigure(0, weight=1)

        tk.Label(green_wrap, text="< GREEN TEAM >", font=(FONT, 10, "bold"),
                 fg=GREEN_NEON, bg=BG_PANEL).grid(row=0, column=0, pady=(8, 4))
        self.green_list = tk.Listbox(green_wrap, font=(FONT, 9),
                                     bg=BG_PANEL, fg=GREEN_NEON,
                                     selectbackground=GREEN_NEON, selectforeground=BG,
                                     relief="flat", borderwidth=0, highlightthickness=0)
        self.green_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def bind_keys(self):
        top = self.winfo_toplevel()
        top.bind("<F5>", lambda e: self.start())
        top.bind("<F12>", lambda e: self.clear_all())
        top.bind("<Return>", lambda e: self.add_player())

    def set_ip(self):
        ip = self.ip_var.get().strip()
        if not ip:
            messagebox.showerror("Error", "IP cannot be empty.")
            return
        if hasattr(self.udp, "set_target_ip"):
            self.udp.set_target_ip(ip)
        messagebox.showinfo("Network", f"UDP target set to {ip}")

    def lookup(self):
        pid = self.parse_int(self.player_id_var.get(), "Player ID")
        if pid is None:
            return
        codename = self.db.get_codename(pid)
        if codename:
            self.codename_var.set(codename)
        else:
            self.codename_var.set("")
            messagebox.showinfo("Not Found", "Player not found. Enter a codename manually.")

    def add_player(self):
        team = self.team_var.get().strip()
        pid = self.parse_int(self.player_id_var.get(), "Player ID")
        if pid is None:
            return
        codename = self.codename_var.get().strip()
        if not codename:
            messagebox.showerror("Error", "Codename is required.")
            return
        eid = self.parse_int(self.equipment_id_var.get(), "Hardware ID")
        if eid is None:
            return

        target = self.red_team if team == "Red" else self.green_team
        if len(target) >= MAX_PER_TEAM:
            messagebox.showerror("Team Full", f"{team} team is full.")
            return

        existing = self.db.get_codename(pid)
        if existing:
            codename = existing
            self.codename_var.set(existing)
        else:
            self.db.add_player(pid, codename)

        target.append(PlayerRow(player_id=pid, codename=codename, equipment_id=eid))
        self.refresh_lists()
        self.udp.send_equipment_id(eid)

        self.player_id_var.set("")
        self.codename_var.set("")
        self.equipment_id_var.set("")

    def clear_all(self):
        self.red_team.clear()
        self.green_team.clear()
        self.refresh_lists()

    def start(self):
        self.on_start_game(self.red_team, self.green_team)

    def refresh_lists(self):
        self.red_list.delete(0, "end")
        self.green_list.delete(0, "end")
        for p in self.red_team:
            self.red_list.insert("end", f" {p.player_id} | {p.codename} | hw:{p.equipment_id}")
        for p in self.green_team:
            self.green_list.insert("end", f" {p.player_id} | {p.codename} | hw:{p.equipment_id}")

    @staticmethod
    def parse_int(value, field):
        try:
            return int(value.strip())
        except Exception:
            messagebox.showerror("Error", f"{field} must be a number.")
            return None