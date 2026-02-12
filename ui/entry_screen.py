# entry_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass

MAX_PER_TEAM = 15


@dataclass
class PlayerRow:
    player_id: int
    codename: str
    equipment_id: int


class PlayerEntryScreen(ttk.Frame):
    """
    Sprint 2 UI:
      - operator enters player_id, DB lookup codename
      - if not found, operator types codename and it gets added to DB
      - operator enters equipment_id, UDP send equipment_id to port 7500 (mock here)
      - two teams: red/green, max 15 per team
      - F5 start button / key
      - F12 clear button / key
      - change network address (UDP target IP field)
    """

    def __init__(self, master, db, udp, on_start_game):
        super().__init__(master)
        self.db = db
        self.udp = udp
        self.on_start_game = on_start_game

        self.red_team: list[PlayerRow] = []
        self.green_team: list[PlayerRow] = []

        self._build_ui()
        self._bind_keys()
        self._refresh_lists()

    # UI
    def _build_ui(self):
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Player Entry", font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

        # Network config
        net = ttk.LabelFrame(self, text="Network / UDP Settings")
        net.grid(row=1, column=0, sticky="ew", padx=16, pady=6)
        net.grid_columnconfigure(1, weight=1)

        ttk.Label(net, text="Target IP:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.ip_var = tk.StringVar(value=getattr(self.udp, "target_ip", "127.0.0.1"))
        ttk.Entry(net, textvariable=self.ip_var, width=22).grid(row=0, column=1, sticky="w", padx=10, pady=8)
        ttk.Button(net, text="Set IP", command=self._set_ip).grid(row=0, column=2, padx=10, pady=8)

        content = ttk.Frame(self)
        content.grid(row=2, column=0, sticky="nsew", padx=16, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        self._build_form(content)
        self._build_rosters(content)

        # Bottom buttons
        bottom = ttk.Frame(self)
        bottom.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        ttk.Button(bottom, text="Clear All (F12)", command=self._clear_all).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(bottom, text="Start (F5)", command=self._start).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _build_form(self, parent):
        form = ttk.LabelFrame(parent, text="Add Player")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        for c in range(3):
            form.grid_columnconfigure(c, weight=1)

        # Team
        ttk.Label(form, text="Team:").grid(row=0, column=0, sticky="e", padx=8, pady=8)
        self.team_var = tk.StringVar(value="Red")
        ttk.Combobox(form, textvariable=self.team_var, values=["Red", "Green"], state="readonly", width=10)\
            .grid(row=0, column=1, sticky="w", padx=8, pady=8)

        # Player ID
        ttk.Label(form, text="Player ID:").grid(row=1, column=0, sticky="e", padx=8, pady=8)
        self.player_id_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.player_id_var).grid(row=1, column=1, sticky="ew", padx=8, pady=8)
        ttk.Button(form, text="Lookup", command=self._lookup).grid(row=1, column=2, sticky="ew", padx=8, pady=8)

        # Codename
        ttk.Label(form, text="Codename:").grid(row=2, column=0, sticky="e", padx=8, pady=8)
        self.codename_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.codename_var).grid(row=2, column=1, sticky="ew", padx=8, pady=8)
        ttk.Label(form, text="(auto-fill if found)").grid(row=2, column=2, sticky="w", padx=8, pady=8)

        # Equipment ID
        ttk.Label(form, text="Equipment ID:").grid(row=3, column=0, sticky="e", padx=8, pady=8)
        self.equipment_id_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.equipment_id_var).grid(row=3, column=1, sticky="ew", padx=8, pady=8)

        # Add player button
        ttk.Button(form, text="Add Player", command=self._add_player)\
            .grid(row=4, column=0, columnspan=3, sticky="ew", padx=8, pady=(10, 8))

        ttk.Label(form, text="Tip: Press Enter to Add after filling fields.", font=("Arial", 9))\
            .grid(row=5, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 8))

    def _build_rosters(self, parent):
        roster = ttk.Frame(parent)
        roster.grid(row=0, column=1, sticky="nsew")
        roster.grid_columnconfigure(0, weight=1)
        roster.grid_columnconfigure(1, weight=1)
        roster.grid_rowconfigure(1, weight=1)

        ttk.Label(roster, text="Rosters", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        red_frame = ttk.LabelFrame(roster, text=f"Red Team (max {MAX_PER_TEAM})")
        red_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        red_frame.grid_rowconfigure(0, weight=1)
        red_frame.grid_columnconfigure(0, weight=1)

        green_frame = ttk.LabelFrame(roster, text=f"Green Team (max {MAX_PER_TEAM})")
        green_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        green_frame.grid_rowconfigure(0, weight=1)
        green_frame.grid_columnconfigure(0, weight=1)

        self.red_list = tk.Listbox(red_frame, height=14)
        self.red_list.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.green_list = tk.Listbox(green_frame, height=14)
        self.green_list.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def _bind_keys(self):
        top = self.winfo_toplevel()
        top.bind("<F5>", lambda e: self._start())
        top.bind("<F12>", lambda e: self._clear_all())
        top.bind("<Return>", lambda e: self._add_player())

    # Action stuff
    def _set_ip(self):
        ip = self.ip_var.get().strip()
        if not ip:
            messagebox.showerror("Network Error", "Target IP cannot be empty.")
            return

        if hasattr(self.udp, "set_target_ip"):
            self.udp.set_target_ip(ip)

        messagebox.showinfo("Network", f"UDP target IP set to {ip}")

    def _lookup(self):
        pid = self._parse_int(self.player_id_var.get(), "Player ID")
        if pid is None:
            return

        codename = self.db.get_codename(pid)
        if codename:
            self.codename_var.set(codename)
        else:
            self.codename_var.set("")
            messagebox.showinfo("Player Not Found", "Player ID not found. Enter a new codename and press Add Player.")

    def _add_player(self):
        team = self.team_var.get().strip()
        pid = self._parse_int(self.player_id_var.get(), "Player ID")
        if pid is None:
            return

        codename = self.codename_var.get().strip()
        if not codename:
            messagebox.showerror("Input Error", "Codename is required.")
            return

        eid = self._parse_int(self.equipment_id_var.get(), "Equipment ID")
        if eid is None:
            return

        target = self.red_team if team == "Red" else self.green_team
        if len(target) >= MAX_PER_TEAM:
            messagebox.showerror("Team Full", f"{team} already has {MAX_PER_TEAM} players.")
            return

        # DB lookup, and if not found, add new codename
        existing = self.db.get_codename(pid)
        if existing:
            codename = existing
            self.codename_var.set(existing)
        else:
            self.db.add_player(pid, codename)

        # Add to roster list
        target.append(PlayerRow(player_id=pid, codename=codename, equipment_id=eid))
        self._refresh_lists()

        # after equipment id entered, send equipment id
        self.udp.send_equipment_id(eid)

        # Clear form for next entry
        self.player_id_var.set("")
        self.codename_var.set("")
        self.equipment_id_var.set("")

    def _clear_all(self):
        self.red_team.clear()
        self.green_team.clear()
        self._refresh_lists()

    def _start(self):
        self.on_start_game(self.red_team, self.green_team)

    # Helpers
    def _refresh_lists(self):
        self.red_list.delete(0, "end")
        self.green_list.delete(0, "end")

        for p in self.red_team:
            self.red_list.insert("end", f"{p.player_id} | {p.codename} | eq:{p.equipment_id}")

        for p in self.green_team:
            self.green_list.insert("end", f"{p.player_id} | {p.codename} | eq:{p.equipment_id}")

    @staticmethod
    def _parse_int(value: str, field: str):
        try:
            return int(value.strip())
        except Exception:
            messagebox.showerror("Input Error", f"{field} must be an integer.")
            return None