#!/usr/bin/env python
import sys
import os
import subprocess
import threading
import json
import zipfile
import shutil
import re
from datetime import datetime
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = "replace-with-your-secure-secret-key"
app.config['APP_RUNNING'] = False

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AdminDashboard")

# Paths & constants
PYTHON_EXEC       = sys.executable
INSTALL_DIR       = os.path.dirname(os.path.abspath(__file__))
GITHUB_REPO       = "https://github.com/Retexc/BdeB-GTFS.git"
CSS_FILE_PATH     = "./static/index.css"
STATIC_IMAGES_DIR = "./static/assets/images"
UPDATE_INFO_FILE  = "./gtfs_update_info.json"

main_app_logs = []
app_process    = None

def capture_app_logs(process):
    """Continuously read stdout from the main app process."""
    while True:
        line = process.stdout.readline()
        if not line:
            break
        main_app_logs.append(line.rstrip())
    app.config['APP_RUNNING'] = False
    logger.info("Main app process ended.")

# ----- GTFS update info persistence -----

def load_gtfs_update_info():
    if os.path.exists(UPDATE_INFO_FILE):
        try:
            with open(UPDATE_INFO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"stm": None, "exo": None}

def save_gtfs_update_info(info):
    try:
        with open(UPDATE_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)
    except Exception as e:
        logger.error("Error saving GTFS info: %s", e)

# ----- Background slot utilities -----

def parse_slots_from_css(css_path):
    slots = [{"path": None, "start": None, "end": None} for _ in range(4)]
    if not os.path.isfile(css_path):
        return slots
    content = open(css_path, 'r', encoding='utf-8').read()
    block = re.search(r"/\*\s*MULTISLOT:\s*(.*?)\*/", content, re.DOTALL|re.IGNORECASE)
    if not block:
        return slots
    for line in block.group(1).strip().splitlines():
        m = re.search(r"SLOT(\d+):\s+(.+?)\s+from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", line)
        if m:
            idx = int(m.group(1)) - 1
            if 0 <= idx < 4:
                slots[idx]["path"]  = m.group(2).strip()
                try: slots[idx]["start"] = datetime.strptime(m.group(3), "%Y-%m-%d").date()
                except: pass
                try: slots[idx]["end"]   = datetime.strptime(m.group(4), "%Y-%m-%d").date()
                except: pass
    return slots

def write_slots_to_css(css_path, slots):
    lines = ["MULTISLOT:"]
    for i, s in enumerate(slots, start=1):
        path = s["path"] or ""
        start = s["start"].strftime("%Y-%m-%d") if s["start"] else "0000-00-00"
        end   = s["end"].strftime("%Y-%m-%d")   if s["end"]   else "0000-00-00"
        lines.append(f"SLOT{i}: {path} from {start} to {end}")
    new_block = "/* " + "\n".join(lines) + " */"
    if not os.path.isfile(css_path):
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(new_block + "\n")
        return
    content = open(css_path, 'r', encoding='utf-8').read()
    updated, count = re.subn(r"/\*\s*MULTISLOT:.*?\*/", new_block,
                             content, flags=re.DOTALL|re.IGNORECASE)
    if count:
        open(css_path, 'w', encoding='utf-8').write(updated)
    else:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write("\n\n" + new_block + "\n")

def copy_to_static_folder(src_path):
    os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)
    dest = os.path.join(STATIC_IMAGES_DIR, os.path.basename(src_path))
    try:
        shutil.copy2(src_path, dest)
    except shutil.SameFileError:
        pass
    return dest.replace("\\", "/")

# ----- Routes -----

@app.route("/")
def admin_home():
    return render_template("home.html")

@app.route("/admin/background")
def admin_background():
    slots = parse_slots_from_css(CSS_FILE_PATH)
    return render_template("background.html", slots=slots)

@app.route("/admin/update_background", methods=["POST"])
def update_background():
    slot_num = request.form.get("slot_number")
    start_str = request.form.get("startDate")
    end_str   = request.form.get("endDate")
    file      = request.files.get("bgFile")

    if not slot_num:
        flash("Aucun slot n'a été sélectionné", "warning")
        return redirect(url_for("admin_background"))

    try:
        idx = int(slot_num) - 1
        if idx not in range(4):
            raise ValueError()
    except:
        flash("Numéro de slot invalide", "danger")
        return redirect(url_for("admin_background"))

    new_path = None
    if file and file.filename:
        os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)
        save_path = os.path.join(STATIC_IMAGES_DIR, file.filename)
        file.save(save_path)
        new_path = f"./static/assets/images/{file.filename}"

    slots = parse_slots_from_css(CSS_FILE_PATH)
    if new_path:
        slots[idx]["path"] = new_path
    try:
        slots[idx]["start"] = datetime.strptime(start_str, "%Y-%m-%d").date()
    except:
        pass
    try:
        slots[idx]["end"] = datetime.strptime(end_str, "%Y-%m-%d").date()
    except:
        pass

    write_slots_to_css(CSS_FILE_PATH, slots)
    flash(f"Background du slot {idx+1} mis à jour avec succès !", "success")
    return redirect(url_for("admin_background"))

@app.route("/admin/settings")
def admin_settings():
    info = load_gtfs_update_info()
    try:
        local  = subprocess.check_output(
            ["git", "-C", INSTALL_DIR, "rev-parse", "HEAD"], universal_newlines=True
        ).strip()
        remote = subprocess.check_output(
            ["git", "ls-remote", GITHUB_REPO, "HEAD"],
            shell=True, universal_newlines=True
        ).split()[0]
        update_available = (local != remote)
    except:
        update_available = False

    last_checked = datetime.now().strftime("%Y‑%m‑%d %H:%M:%S")
    return render_template(
        "settings.html",
        update_info      = info,
        update_available = update_available,
        last_checked     = last_checked
    )

@app.route("/admin/app_update", methods=["POST"])
def admin_app_update():
    try:
        if os.path.isdir(os.path.join(INSTALL_DIR, ".git")):
            subprocess.check_call(["git", "-C", INSTALL_DIR, "pull"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        else:
            subprocess.check_call(["git", "clone", GITHUB_REPO, INSTALL_DIR],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        subprocess.check_call([PYTHON_EXEC, "-m", "pip", "install", "--upgrade", "pip"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        req = os.path.join(INSTALL_DIR, "requirements.txt")
        if os.path.exists(req):
            subprocess.check_call([PYTHON_EXEC, "-m", "pip", "install", "-r", req],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        flash(f"Application mise à jour avec succès ! ({datetime.now().strftime('%Y‑%m‑%d %H:%M:%S')})", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Erreur lors de la mise à jour : {e}", "danger")

    return redirect(url_for("admin_settings"))

@app.route("/admin/update_gtfs", methods=["POST"])
def admin_update_gtfs():
    transport = request.form.get("transport")
    z         = request.files.get("gtfs_zip")

    if not transport or not z or z.filename == "":
        flash("Aucun fichier sélectionné.", "danger")
        return redirect(url_for("admin_settings"))

    if not z.filename.lower().endswith(".zip"):
        flash("Merci de télécharger un fichier ZIP GTFS.", "warning")
        return redirect(url_for("admin_settings"))

    tmp = os.path.join(os.getcwd(), z.filename)
    z.save(tmp)

    if transport == "stm":
        target = os.path.join(os.getcwd(), "STM")
    else:
        target = os.path.join(os.getcwd(), "Exo", "Train")
    os.makedirs(target, exist_ok=True)

    try:
        with zipfile.ZipFile(tmp, "r") as archive:
            archive.extractall(target)
    except Exception as e:
        flash(f"Erreur d'extraction : {e}", "danger")
        os.remove(tmp)
        return redirect(url_for("admin_settings"))
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    info = load_gtfs_update_info()
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info[transport] = now
    save_gtfs_update_info(info)

    flash(f"Fichiers GTFS {transport.upper()} mis à jour avec succès ! ({now})", "success")
    return redirect(url_for("admin_settings"))

@app.route("/admin/start", methods=["POST"])
def admin_start():
    global app_process
    if not app.config['APP_RUNNING']:
        try:
            cmd = [
                PYTHON_EXEC, "-u", "-m", "waitress",
                "--host=127.0.0.1", "--port=5000", "app:app"
            ]
            app_process = subprocess.Popen(
                cmd, cwd=INSTALL_DIR,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            app.config['APP_RUNNING'] = True
            main_app_logs.append(f"{datetime.now()} - Main app started.")
            threading.Thread(target=capture_app_logs, args=(app_process,), daemon=True).start()
            return jsonify({'status': 'started'}), 200
        except Exception as e:
            logger.error("Error starting main app: %s", e)
            return jsonify({'status': 'error', 'error': str(e)}), 500

    return jsonify({'status': 'already_running'}), 200

@app.route("/admin/stop", methods=["POST"])
def admin_stop():
    global app_process
    if app.config['APP_RUNNING'] and app_process:
        try:
            app_process.terminate()
            app_process.wait(timeout=10)
            app.config['APP_RUNNING'] = False
            main_app_logs.append(f"{datetime.now()} - Main app stopped.")
            return jsonify({'status': 'stopped'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'error': str(e)}), 500

    return jsonify({'status': 'not_running'}), 200

@app.route("/admin/status")
def admin_status():
    return jsonify({"running": app.config['APP_RUNNING']})

@app.route("/admin/logs_data")
def logs_data():
    return "\n".join(main_app_logs)

if __name__ == "__main__":
    # Run the admin dashboard on port 5001; the main display app runs on 5000 via /admin/start
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5001)
