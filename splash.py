# splash.py
import os
import tkinter as tk
from PIL import Image, ImageTk

# COLOR THEMES:
BG = "#0a0a0a"
GOLD = "#f5c400"
RED_NEON = "#e83030"
DIM = "#aaaaaa"
FONT_MONO = "Courier"

class SplashScreen(tk.Toplevel):
    # shows for 3 seconds (sprint 2)
    def __init__(self, master: tk.Tk, logo_path: str, on_done, ms: int = 3000):
        super().__init__(master)
        self._on_done = on_done

        self.configure(bg=BG)
        self.overrideredirect(True)

        w, h = 820, 480
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # draw scanlines + gold border on a canvas behind everything
        self._canvas = tk.Canvas(self, width=w, height=h, bg=BG, highlightthickness=0)
        self._canvas.place(x=0, y=0)
        for i in range(0, h, 4):
            self._canvas.create_line(0, i, w, i, fill="#ffffff", stipple="gray12")
        self._canvas.create_rectangle(6, 6, w-6, h-6, outline=GOLD, width=2)

        # load logo
        self.logo_img = None
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).convert("RGBA")
                img.thumbnail((720, 340))
                self.logo_img = ImageTk.PhotoImage(img)
            except Exception:
                self.logo_img = None

        frame = tk.Frame(self, bg=BG)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.logo_img:
            tk.Label(frame, image=self.logo_img, bg=BG).pack(pady=(0, 14))
        else:
            tk.Label(frame, text="PHOTON", font=(FONT_MONO, 52, "bold"),
                     fg=GOLD, bg=BG).pack(pady=(0, 6))
            tk.Label(frame, text="THE ULTIMATE GAME ON PLANET EARTH",
                     font=(FONT_MONO, 11), fg=RED_NEON, bg=BG).pack()

        # Loading text with animated dots
        self._dot_label = tk.Label(frame, text="LOADING",
                                   font=(FONT_MONO, 11), fg=DIM, bg=BG)
        self._dot_label.pack(pady=(10, 0))
        self._dot_count = 0
        self._blink()

        self.lift()
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))
        self.after(ms, self._finish)

    # Animated dots for loading text
    def _blink(self):
        dots = "." * (self._dot_count % 4)
        self._dot_label.config(text=f"LOADING{dots:<3}")
        self._dot_count += 1
        self.after(400, self._blink)

    def _finish(self):
        try:
            self.destroy()
        finally:
            self._on_done()