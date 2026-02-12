# splash.py
import os
import tkinter as tk
from PIL import Image, ImageTk

class SplashScreen(tk.Toplevel):
    # Sprint 2: splash screen shows for ~3 seconds, then calls on_done().
    def __init__(self, master: tk.Tk, logo_path: str, on_done, ms: int = 3000):
        super().__init__(master)
        self._on_done = on_done

        # Dark background fits for the logo
        self.configure(bg="#000000")
        self.overrideredirect(True)

        # Center window
        w, h = 800, 450
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Load and scale the logo
        self.logo_img = None
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).convert("RGBA")
                img.thumbnail((760, 380))
                self.logo_img = ImageTk.PhotoImage(img)
            except Exception:
                self.logo_img = None

        # Layout
        frame = tk.Frame(self, bg="#000000")
        frame.pack(fill="both", expand=True)

        if self.logo_img:
            tk.Label(frame, image=self.logo_img, bg="#000000").pack(pady=(20, 10))
        else:
            tk.Label(frame, text="PHOTON", font=("Arial", 44, "bold"), fg="white", bg="#000000").pack(pady=(120, 10))
            tk.Label(frame, text="(logo failed to load)", fg="white", bg="#000000").pack()

        tk.Label(frame, text="Loading...", font=("Arial", 12), fg="white", bg="#000000").pack(pady=(5, 0))

        # Bring to the front
        self.lift()
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))

        self.after(ms, self._finish)

    def _finish(self):
        try:
            self.destroy()
        finally:
            self._on_done()