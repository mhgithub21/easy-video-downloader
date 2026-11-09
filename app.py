"""Easy Video Downloader - a simple open-source GUI for yt-dlp.

Only download videos you own, that are in the public domain / Creative Commons,
or that you have permission to download. Respect each site's Terms of Service.
"""
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yt_dlp

try:
    from icon_data import ICON_PNG_B64
except ImportError:  # icon is optional
    ICON_PNG_B64 = None

APP_NAME = "Easy Video Downloader"
HAS_FFMPEG = shutil.which("ffmpeg") is not None
DATA_DIR = Path.home() / ".easy_video_downloader"
SETTINGS_FILE = DATA_DIR / "settings.json"
HISTORY_FILE = DATA_DIR / "history.json"

QUALITIES = {
    "Best available / সেরা মান": ("video", None),
    "1080p": ("video", 1080),
    "720p": ("video", 720),
    "480p": ("video", 480),
    "360p": ("video", 360),
    "Audio only (MP3) / শুধু অডিও": ("audio", None),
}

THEMES = {
    "light": {"bg": "#f3f4f6", "fg": "#111827", "field": "#ffffff", "btn": "#e5e7eb", "accent": "#2563eb"},
    "dark": {"bg": "#1e1e2e", "fg": "#e6e6f0", "field": "#2a2a3c", "btn": "#38384d", "accent": "#3b82f6"},
}


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save_json(path, data):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def open_folder(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:  # noqa: BLE001
        messagebox.showerror(APP_NAME, f"Cannot open folder: {e}")


def build_options(choice, outdir, hook, playlist):
    kind, height = QUALITIES[choice]
    opts = {
        "outtmpl": os.path.join(outdir, "%(title).150s [%(id)s].%(ext)s"),
        "progress_hooks": [hook],
        "noplaylist": not playlist,
        "quiet": True,
        "no_warnings": True,
    }
    if kind == "audio":
        opts["format"] = "bestaudio/best"
        if HAS_FFMPEG:
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
    else:
        limit = f"[height<={height}]" if height else ""
        if HAS_FFMPEG:
            opts["format"] = f"bestvideo{limit}+bestaudio/best{limit}/best"
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = f"best{limit}/best"
    return opts


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("660x580")
        self.minsize(580, 500)
        self._set_icon()

        s = load_json(SETTINGS_FILE, {})
        self.msgs = queue.Queue()
        self.current_url = ""
        self.outdir = tk.StringVar(value=s.get("outdir", str(Path.home() / "Downloads")))
        self.quality = tk.StringVar(value=list(QUALITIES)[0])
        self.playlist = tk.BooleanVar(value=False)
        self.dark = tk.BooleanVar(value=s.get("dark", False))
        self.history = load_json(HISTORY_FILE, [])

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._build_ui()
        self.apply_theme()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._poll)
        if not HAS_FFMPEG:
            self._log("Note: ffmpeg not found. MP3 conversion and high-quality "
                      "merging are disabled. See README to install ffmpeg.")

    # ---------- UI ----------
    def _set_icon(self):
        if ICON_PNG_B64:
            try:
                self._icon = tk.PhotoImage(data=ICON_PNG_B64)
                self.iconphoto(True, self._icon)
            except tk.TclError:
                pass

    def _build_ui(self):
        pad = {"padx": 12, "pady": 4}
        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Label(top, text="Video links (one per line) / ভিডিও লিংক (প্রতি লাইনে একটি)").pack(side="left")
        ttk.Checkbutton(top, text="Dark mode", variable=self.dark, command=self.apply_theme).pack(side="right")

        self.urls = tk.Text(self, height=5, wrap="none", relief="flat", borderwidth=4)
        self.urls.pack(fill="x", **pad)

        row = ttk.Frame(self)
        row.pack(fill="x", **pad)
        ttk.Label(row, text="Quality / মান:").pack(side="left")
        ttk.Combobox(row, textvariable=self.quality, values=list(QUALITIES),
                     state="readonly", width=28).pack(side="left", padx=8)
        ttk.Checkbutton(row, text="Download playlists", variable=self.playlist).pack(side="left", padx=8)

        row2 = ttk.Frame(self)
        row2.pack(fill="x", **pad)
        ttk.Label(row2, text="Save to / সেভ ফোল্ডার:").pack(side="left")
        ttk.Entry(row2, textvariable=self.outdir).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(row2, text="Browse...", command=self._browse).pack(side="left")

        btns = ttk.Frame(self)
        btns.pack(**pad)
        self.btn = ttk.Button(btns, text="Download / ডাউনলোড", command=self._start, style="Accent.TButton")
        self.btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Open folder", command=lambda: open_folder(self.outdir.get())).pack(side="left", padx=4)
        ttk.Button(btns, text="History / ইতিহাস", command=self._show_history).pack(side="left", padx=4)

        self.bar = ttk.Progressbar(self, maximum=100)
        self.bar.pack(fill="x", **pad)
        self.status = ttk.Label(self, text="Ready")
        self.status.pack(anchor="w", **pad)

        self.logbox = tk.Text(self, height=10, state="disabled", wrap="word", relief="flat", borderwidth=4)
        self.logbox.pack(fill="both", expand=True, **pad)

    def apply_theme(self):
        t = THEMES["dark" if self.dark.get() else "light"]
        st = self.style
        self.configure(bg=t["bg"])
        st.configure(".", background=t["bg"], foreground=t["fg"], fieldbackground=t["field"],
                     bordercolor=t["btn"], lightcolor=t["bg"], darkcolor=t["bg"])
        st.configure("TButton", background=t["btn"], foreground=t["fg"], padding=6)
        st.map("TButton", background=[("active", t["accent"])], foreground=[("active", "#ffffff")])
        st.configure("Accent.TButton", background=t["accent"], foreground="#ffffff")
        st.configure("TCheckbutton", background=t["bg"], foreground=t["fg"])
        st.map("TCheckbutton", background=[("active", t["bg"])])
        st.configure("TEntry", fieldbackground=t["field"], foreground=t["fg"])
        st.configure("TCombobox", fieldbackground=t["field"], background=t["btn"], foreground=t["fg"],
                     arrowcolor=t["fg"])
        st.map("TCombobox", fieldbackground=[("readonly", t["field"])], foreground=[("readonly", t["fg"])])
        st.configure("Horizontal.TProgressbar", background=t["accent"], troughcolor=t["field"])
        st.configure("Treeview", background=t["field"], fieldbackground=t["field"], foreground=t["fg"])
        st.configure("Treeview.Heading", background=t["btn"], foreground=t["fg"])
        st.map("Treeview", background=[("selected", t["accent"])], foreground=[("selected", "#ffffff")])
        self.option_add("*TCombobox*Listbox.background", t["field"])
        self.option_add("*TCombobox*Listbox.foreground", t["fg"])
        for w in (self.urls, self.logbox):
            w.configure(bg=t["field"], fg=t["fg"], insertbackground=t["fg"])

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.outdir.get())
        if d:
            self.outdir.set(d)

    def _log(self, text):
        self.logbox.configure(state="normal")
        self.logbox.insert("end", text + "\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")

    def _on_close(self):
        save_json(SETTINGS_FILE, {"dark": self.dark.get(), "outdir": self.outdir.get()})
        self.destroy()

    # ---------- History ----------
    def _show_history(self):
        win = tk.Toplevel(self)
        win.title("Download history / ডাউনলোড ইতিহাস")
        win.geometry("640x360")
        win.configure(bg=THEMES["dark" if self.dark.get() else "light"]["bg"])
        tree = ttk.Treeview(win, columns=("date", "title"), show="headings")
        tree.heading("date", text="Date")
        tree.heading("title", text="Title")
        tree.column("date", width=140, stretch=False)
        tree.column("title", width=480)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        items = list(reversed(self.history))
        for i, h in enumerate(items):
            tree.insert("", "end", iid=str(i), values=(h.get("date", ""), h.get("title", "")))

        def selected():
            sel = tree.selection()
            return items[int(sel[0])] if sel else None

        def open_sel():
            h = selected()
            if h and os.path.isdir(h.get("folder", "")):
                open_folder(h["folder"])

        def copy_url():
            h = selected()
            if h:
                self.clipboard_clear()
                self.clipboard_append(h.get("url", ""))

        def clear():
            if messagebox.askyesno(APP_NAME, "Clear all history? / ইতিহাস মুছে ফেলবেন?", parent=win):
                self.history = []
                save_json(HISTORY_FILE, self.history)
                tree.delete(*tree.get_children())

        bar = ttk.Frame(win)
        bar.pack(pady=(0, 10))
        ttk.Button(bar, text="Open folder", command=open_sel).pack(side="left", padx=4)
        ttk.Button(bar, text="Copy link", command=copy_url).pack(side="left", padx=4)
        ttk.Button(bar, text="Clear", command=clear).pack(side="left", padx=4)

    def _add_history(self, title, url, folder):
        self.history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": title, "url": url, "folder": folder,
        })
        self.history = self.history[-500:]
        save_json(HISTORY_FILE, self.history)

    # ---------- Download ----------
    def _start(self):
        urls = [u.strip() for u in self.urls.get("1.0", "end").splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning(APP_NAME, "Please paste at least one link.\nঅন্তত একটি লিংক দিন।")
            return
        outdir = self.outdir.get()
        try:
            os.makedirs(outdir, exist_ok=True)
        except OSError as e:
            messagebox.showerror(APP_NAME, f"Cannot use folder: {e}")
            return
        self.btn.configure(state="disabled")
        self.bar["value"] = 0
        threading.Thread(
            target=self._worker,
            args=(urls, outdir, self.quality.get(), self.playlist.get()),
            daemon=True,
        ).start()

    def _worker(self, urls, outdir, choice, playlist):
        def hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                if total:
                    pct = d.get("downloaded_bytes", 0) / total * 100
                    speed, eta = d.get("speed"), d.get("eta")
                    txt = f"{pct:.1f}%"
                    if speed:
                        txt += f" - {speed / 1024 / 1024:.2f} MB/s"
                    if eta is not None:
                        txt += f" - ETA {int(eta)}s"
                    self.msgs.put(("progress", pct, txt))
            elif d["status"] == "finished":
                info = d.get("info_dict") or {}
                self.msgs.put(("history", info.get("title") or os.path.basename(d.get("filename", "")),
                               self.current_url, outdir))
                self.msgs.put(("progress", 100, "Processing..."))

        opts = build_options(choice, outdir, hook, playlist)
        for i, url in enumerate(urls, 1):
            self.current_url = url
            self.msgs.put(("log", f"[{i}/{len(urls)}] {url}"))
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                self.msgs.put(("log", "  Done / সম্পন্ন"))
            except Exception as e:  # noqa: BLE001
                self.msgs.put(("log", f"  Error: {e}"))
        self.msgs.put(("done", 0, "All finished / সব শেষ"))

    def _poll(self):
        try:
            while True:
                kind, a, *rest = self.msgs.get_nowait()
                if kind == "progress":
                    self.bar["value"] = a
                    self.status.configure(text=rest[0])
                elif kind == "log":
                    self._log(a)
                elif kind == "history":
                    self._add_history(a, *rest)
                elif kind == "done":
                    self.status.configure(text=rest[0])
                    self.btn.configure(state="normal")
        except queue.Empty:
            pass
        self.after(100, self._poll)


if __name__ == "__main__":
    App().mainloop()
