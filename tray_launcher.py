import os
import sys
import threading
import subprocess
import webbrowser
import tkinter as tk
from PIL import Image, ImageTk

from pystray import Icon, MenuItem, Menu
from PIL import Image
from winotify import Notification, audio

# ───────────────────────────────────────────────────────────────────────────────
# CONFIG
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC       = os.path.join(REPO_ROOT, "src")
ADMIN_APP = "bdeb_gtfs.admin:app"
PY        = sys.executable

admin_proc = None

ICON_PATH = os.path.join(
    REPO_ROOT,
    "src", "bdeb_gtfs", "static", "assets", "icons", "icon.ico"
)
SPLASH_IMG = os.path.join(
    REPO_ROOT,
      "src", "bdeb_gtfs", "static", "assets", "images", "Splash.png"               
)
img = Image.open(ICON_PATH)

# ───────────────────────────────────────────────────────────────────────────────

def show_splash(duration_ms=5000):
    """Display a borderless splash image for `duration_ms` then destroy."""
    root = tk.Tk()
    root.overrideredirect(True)   # no borders
    img = Image.open(SPLASH_IMG)
    tk_img = ImageTk.PhotoImage(img)
    w, h = img.size
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    lbl = tk.Label(root, image=tk_img)
    lbl.pack()
    root.after(duration_ms, root.destroy)
    root.mainloop()

def start_admin():
    global admin_proc
    if admin_proc and admin_proc.poll() is None:
        return
    cmd = [
        PY, "-u", "-m", "waitress",
        "--host=127.0.0.1", "--port=5001",
        ADMIN_APP
    ]
    admin_proc = subprocess.Popen(cmd, cwd=SRC)
    toast = Notification(
        app_id="BdeB-GTFS",
        title="BdeB-GTFS Manager",
        msg="L’application a démarré à l’adresse http://127.0.0.1:5001. Vous pouvez gérer l’application à partir de l’icône de la zone de notification système.",
        icon=ICON_PATH
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()

def stop_admin():
    global admin_proc
    if admin_proc and admin_proc.poll() is None:
        admin_proc.terminate()
        admin_proc.wait()
        toast = Notification(
            app_id="BdeB-GTFS",
            title="BdeB-GTFS Manager",
            msg="L’application a été arrêtée.",
            icon=ICON_PATH
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()        

def restart_admin(icon, item):
    stop_admin()
    start_admin()

def exit_app(icon, item):
    stop_admin()
    icon.stop()

    

# ───────────────────────────────────────────────────────────────────────────────
def create_tray():
    menu = Menu(
        MenuItem("Redemarrer l'application", lambda icon, item: restart_admin()),
        Menu.SEPARATOR,
        MenuItem("Quitter l'application",          exit_app)
    )

    icon = Icon("BdeB-GTFS Manager", img, "BdeB-GTFS Admin", menu)

    # auto-start admin + open browser
    def _boot():
        start_admin()
        webbrowser.open("http://127.0.0.1:5001")

    threading.Thread(target=_boot, daemon=True).start()
    return icon

# ───────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.environ["PYTHONPATH"] = SRC
    show_splash()
    tray_icon = create_tray()
    tray_icon.run()
