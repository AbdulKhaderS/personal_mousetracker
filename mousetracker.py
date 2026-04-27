"""
mouse_tracker.py
================
Real-time mouse coordinate tracker for pyautogui coordinate mapping.
- Displays live X, Y coordinates as you move the mouse
- Press SPACEBAR to capture and save current coordinates
- Press C to copy latest coordinates to clipboard
- Press ENTER to clear the saved list
- All captured coordinates shown in log with index numbers

Requirements:
    pip install pyautogui keyboard

Run:
    python mouse_tracker.py
"""

import tkinter as tk
from tkinter import scrolledtext
import pyautogui
import threading
import time

# ── Storage for captured coordinates ──────────────────────────────────────────
captured_coords = []

# ──────────────────────────────────────────────────────────────────────────────
# MAIN GUI CLASS
# ──────────────────────────────────────────────────────────────────────────────

class MouseTrackerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🖱 Mouse Coordinate Tracker")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)  # Always on top

        # Colors (dark theme matching your Navision tool)
        self.BG       = "#1e1e2e"
        self.FG       = "#cdd6f4"
        self.ACCENT   = "#89b4fa"
        self.SUCCESS  = "#a6e3a1"
        self.WARNING  = "#f9e2af"
        self.ERROR    = "#f38ba8"
        self.SURFACE  = "#313244"

        self._build_ui()
        self._position_window()
        self._start_tracking()
        self._bind_keys()

    # ── POSITION window bottom-right corner ──────────────────────────────────
    def _position_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w  = self.root.winfo_width()
        h  = self.root.winfo_height()
        x  = sw - w - 20
        y  = sh - h - 60
        self.root.geometry(f"+{x}+{y}")

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.configure(bg=self.BG)

        # ── Title ────────────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="🖱 Mouse Coordinate Tracker",
            font=("Segoe UI", 12, "bold"),
            bg=self.BG, fg=self.ACCENT
        ).pack(pady=(14, 2))

        tk.Label(
            self.root,
            text="Move mouse over Navision • Press SPACE to capture",
            font=("Segoe UI", 8),
            bg=self.BG, fg="#7f849c"
        ).pack()

        # ── Live coordinate display ───────────────────────────────────────────
        coord_frame = tk.Frame(self.root, bg=self.SURFACE, padx=20, pady=14)
        coord_frame.pack(fill="x", padx=16, pady=12)

        tk.Label(
            coord_frame, text="LIVE POSITION",
            font=("Segoe UI", 8, "bold"),
            bg=self.SURFACE, fg="#7f849c"
        ).pack()

        self.lbl_coords = tk.Label(
            coord_frame,
            text="X: ----   Y: ----",
            font=("Consolas", 22, "bold"),
            bg=self.SURFACE, fg=self.SUCCESS
        )
        self.lbl_coords.pack()

        self.lbl_count = tk.Label(
            coord_frame,
            text="Captured: 0 points",
            font=("Segoe UI", 8),
            bg=self.SURFACE, fg="#7f849c"
        )
        self.lbl_count.pack(pady=(4, 0))

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.btn_capture = tk.Button(
            btn_frame,
            text="📌 Capture (SPACE)",
            font=("Segoe UI", 9, "bold"),
            bg=self.ACCENT, fg="#1e1e2e",
            activebackground="#74c7ec",
            relief="flat", cursor="hand2", pady=7,
            command=self._capture
        )
        self.btn_capture.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_copy = tk.Button(
            btn_frame,
            text="📋 Copy Last (C)",
            font=("Segoe UI", 9),
            bg=self.SURFACE, fg=self.FG,
            activebackground="#45475a",
            relief="flat", cursor="hand2", pady=7,
            command=self._copy_last
        )
        self.btn_copy.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # ── Log box ───────────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="Captured Coordinates:",
            font=("Segoe UI", 9, "bold"),
            bg=self.BG, fg="#7f849c", anchor="w"
        ).pack(fill="x", padx=18, pady=(4, 0))

        self.log_box = scrolledtext.ScrolledText(
            self.root,
            state="disabled",
            bg="#181825", fg=self.FG,
            font=("Consolas", 9),
            relief="flat", wrap="word",
            width=44, height=10
        )
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(2, 4))

        self.log_box.tag_config("coord",   foreground=self.SUCCESS)
        self.log_box.tag_config("info",    foreground=self.ACCENT)
        self.log_box.tag_config("warning", foreground=self.WARNING)

        # ── Clear button ──────────────────────────────────────────────────────
        self.btn_clear = tk.Button(
            self.root,
            text="🗑 Clear List (ENTER)",
            font=("Segoe UI", 8),
            bg=self.BG, fg="#7f849c",
            activebackground=self.SURFACE,
            relief="flat", cursor="hand2",
            command=self._clear
        )
        self.btn_clear.pack(pady=(0, 4))

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="SPACE = Capture  •  C = Copy  •  ENTER = Clear",
            font=("Segoe UI", 7),
            bg=self.BG, fg="#45475a"
        ).pack(pady=(0, 10))

    # ── BIND keyboard shortcuts ───────────────────────────────────────────────
    def _bind_keys(self):
        self.root.bind("<space>",  lambda e: self._capture())
        self.root.bind("<Return>", lambda e: self._clear())
        self.root.bind("<c>",      lambda e: self._copy_last())
        self.root.bind("<C>",      lambda e: self._copy_last())

    # ── START live tracking thread ────────────────────────────────────────────
    def _start_tracking(self):
        self._tracking = True
        t = threading.Thread(target=self._track_loop, daemon=True)
        t.start()

    def _track_loop(self):
        """Updates coordinate label every 50ms."""
        while self._tracking:
            try:
                x, y = pyautogui.position()
                self.root.after(0, self._update_display, x, y)
            except Exception:
                pass
            time.sleep(0.05)  # 20 updates per second

    def _update_display(self, x: int, y: int):
        self.lbl_coords.configure(text=f"X: {x:<6}  Y: {y:<6}")
        self._last_x = x
        self._last_y = y

    # ── CAPTURE current position ──────────────────────────────────────────────
    def _capture(self):
        try:
            x, y = pyautogui.position()
        except Exception:
            x = getattr(self, "_last_x", 0)
            y = getattr(self, "_last_y", 0)

        idx = len(captured_coords) + 1
        captured_coords.append((x, y))

        # Update count label
        self.lbl_count.configure(text=f"Captured: {len(captured_coords)} points")

        # Log it
        msg = f"[{idx:02d}]  ({x}, {y})"
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n", "coord")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

        # Auto-copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(f"({x}, {y})")
        self.root.update()

        # Flash feedback
        self.lbl_coords.configure(fg=self.ACCENT)
        self.root.after(200, lambda: self.lbl_coords.configure(fg=self.SUCCESS))

        print(f"Captured [{idx:02d}]: ({x}, {y})")

    # ── COPY last coordinate to clipboard ────────────────────────────────────
    def _copy_last(self):
        if not captured_coords:
            self._log_info("⚠ Nothing captured yet!")
            return
        x, y = captured_coords[-1]
        self.root.clipboard_clear()
        self.root.clipboard_append(f"({x}, {y})")
        self.root.update()
        self._log_info(f"✔ Copied: ({x}, {y})")

    # ── CLEAR the list ────────────────────────────────────────────────────────
    def _clear(self):
        captured_coords.clear()
        self.lbl_count.configure(text="Captured: 0 points")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self._log_info("🗑 List cleared.")

    # ── LOG info message ──────────────────────────────────────────────────────
    def _log_info(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n", "info")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── PRINT all captured on close ───────────────────────────────────────────
    def on_close(self):
        self._tracking = False
        if captured_coords:
            print("\n" + "═" * 40)
            print(" ALL CAPTURED COORDINATES:")
            print("═" * 40)
            for i, (x, y) in enumerate(captured_coords, 1):
                print(f"  [{i:02d}]  ({x}, {y})")
            print("═" * 40)
            # Print as Python dict format (ready to paste in your script!)
            print("\n# Ready to paste in navision_automation.py:")
            print("ITEM_COORDS = {")
            for i, (x, y) in enumerate(captured_coords, 1):
                print(f'    "Item {i}": ({x}, {y}),')
            print("}")
        self.root.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()