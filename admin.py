#!/usr/bin/env python
import sys
import os
import subprocess
import threading
from datetime import datetime
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import re
import json
import shutil
import zipfile

app = Flask(__name__)
app.secret_key = "replace-with-your-secure-secret-key" 

app.config['APP_RUNNING'] = False
main_app_logs = []  
app_process = None  

PYTHON_EXEC = sys.executable

CSS_FILE_PATH = "./static/index.css"
STATIC_IMAGES_DIR = "./static/assets/images"

GITHUB_REPO = "https://github.com/Retexc/BdeB-GTFS.git"
INSTALL_DIR   = os.path.dirname(os.path.abspath(__file__))
UPDATE_INFO_FILE = "./gtfs_update_info.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AdminDashboard")

def capture_app_logs(process):
    while True:
        line = process.stdout.readline()
        if not line:
            break
        main_app_logs.append(line.rstrip())
    app.config['APP_RUNNING'] = False
    logger.info("Main app process ended.")

UPDATE_INFO_FILE = "./gtfs_update_info.json"

def load_gtfs_update_info():
    if os.path.exists(UPDATE_INFO_FILE):
        try:
            with open(UPDATE_INFO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"stm": None, "exo": None}

def save_gtfs_update_info(info):
    try:
        with open(UPDATE_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
    except Exception as e:
        print("Error saving GTFS info:", e)    

# ----------------------------
# Routes for the Admin Dashboard
# ----------------------------

@app.route("/")
def admin_dashboard():
    return render_template("home.html")

@app.route("/admin/background")
def admin_background():
    slots = parse_slots_from_css(CSS_FILE_PATH)
    return render_template("background.html", slots=slots)

@app.route("/admin/settings")
def admin_settings():

    info = load_gtfs_update_info()


    try:
        local  = subprocess.check_output(
            ["git", "-C", INSTALL_DIR, "rev-parse", "HEAD"],
            universal_newlines=True
        ).strip()
        remote = subprocess.check_output(
            ["git", "ls-remote", GITHUB_REPO, "HEAD"],
            shell=True,
            universal_newlines=True
        ).split()[0]
        update_available = (local != remote)
    except Exception:
        update_available = False

    last_checked = datetime.now().strftime("%Y‑%m‑%d %H:%M:%S")


    return render_template(
      "settings.html",
      update_info       = info,
      update_available  = update_available,
      last_checked      = last_checked,
    )

@app.route("/admin/app_update", methods=["POST"])
def admin_app_update():
    try:
        # pull if already cloned, otherwise clone
        if os.path.isdir(os.path.join(INSTALL_DIR, ".git")):
            subprocess.check_call(
              ["git", "-C", INSTALL_DIR, "pull"],
              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
        else:
            subprocess.check_call(
              ["git", "clone", GITHUB_REPO, INSTALL_DIR],
              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )

        # upgrade pip + install requirements
        subprocess.check_call(
          [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
          stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        req = os.path.join(INSTALL_DIR, "requirements.txt")
        if os.path.exists(req):
            subprocess.check_call(
              [sys.executable, "-m", "pip", "install", "-r", req],
              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )

        flash(f"Application mise à jour avec succès ! ({datetime.now().strftime('%Y‑%m‑%d %H:%M:%S')})", "success")

    except subprocess.CalledProcessError as e:
        flash(f"Erreur lors de la mise à jour : {e}", "danger")

    return redirect(url_for("admin_settings"))



@app.route("/admin/start", methods=["POST"])
def admin_start():
    global app_process
    if not app.config['APP_RUNNING']:
        try:
            cmd = [
                PYTHON_EXEC, "-u", "-m", "waitress",
                "--host=127.0.0.1",
                "--port=5000",
                "app:app"
            ]
            app_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            app.config['APP_RUNNING'] = True
            main_app_logs.append(f"{datetime.now()} - Main app started via Waitress.")
            threading.Thread(target=capture_app_logs, args=(app_process,), daemon=True).start()
            logger.info("Main app has been started via Waitress.")
            return jsonify({'status': 'started'}), 200
        except Exception as e:
            logger.error(f"Error starting main app: {str(e)}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    else:
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
            logger.info("Main app has been stopped.")
            return jsonify({'status': 'stopped'}), 200
        except Exception as e:
            logger.error(f"Error stopping main app: {str(e)}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    else:
        return jsonify({'status': 'not_running'}), 200
    
@app.route('/admin/status')
def admin_status():
    return jsonify({"running": app.config['APP_RUNNING']})

@app.route("/admin/logs_data")
def logs_data():
    return "\n".join(main_app_logs)

# ----------------------------
#  Background Management Functions 
# ----------------------------

def parse_slots_from_css(css_path):
    """
    Reads the CSS file and extracts the multislot data defined in a comment block.
    Returns a list of 4 dictionaries with keys: 'path', 'start', 'end'
    """
    slots = [{"path": None, "start": None, "end": None} for _ in range(4)]
    if not os.path.isfile(css_path):
        return slots
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    pattern_block = re.compile(r"/\*\s*MULTISLOT:\s*(.*?)\*/", re.IGNORECASE | re.DOTALL)
    match_block = pattern_block.search(css_content)
    if not match_block:
        return slots
    block_text = match_block.group(1).strip()
    line_pattern = re.compile(
        r"SLOT(\d+):\s+(.+?)\s+from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", 
        re.IGNORECASE
    )
    for line in block_text.splitlines():
        line = line.strip()
        m = line_pattern.search(line)
        if m:
            slot_index = int(m.group(1))
            slot_path = m.group(2).strip()
            start_str = m.group(3)
            end_str = m.group(4)
            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            except ValueError:
                start_date = None
            try:
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                end_date = None
            idx = slot_index - 1
            if 0 <= idx < 4:
                slots[idx]["path"] = slot_path
                slots[idx]["start"] = start_date
                slots[idx]["end"] = end_date
    return slots

def write_slots_to_css(css_path, slots):
    lines = ["MULTISLOT:"]
    for i, slot in enumerate(slots, start=1):
        path_str = slot["path"] if slot["path"] else ""
        start_str = slot["start"].strftime("%Y-%m-%d") if slot["start"] else "0000-00-00"
        end_str = slot["end"].strftime("%Y-%m-%d") if slot["end"] else "0000-00-00"
        line = f"SLOT{i}: {path_str} from {start_str} to {end_str}"
        lines.append(line)
    block_text = "\n".join(lines)
    new_block = f"/* {block_text} */"
    
    if not os.path.isfile(css_path):
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(new_block + "\n")
        return

    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    pattern_block = re.compile(r"/\*\s*MULTISLOT:.*?\*/", re.IGNORECASE | re.DOTALL)
    new_css, count = pattern_block.subn(new_block, css_content)
    if count == 0:
        new_css = css_content.rstrip() + "\n\n" + new_block + "\n"
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(new_css)

def copy_to_static_folder(src_path):

    if not os.path.isdir(STATIC_IMAGES_DIR):
        os.makedirs(STATIC_IMAGES_DIR)
    filename = os.path.basename(src_path)
    dest_path = os.path.join(STATIC_IMAGES_DIR, filename)
    src_abs = os.path.abspath(src_path)
    dest_abs = os.path.abspath(dest_path)
    if os.path.exists(dest_path):
        try:
            if os.path.samefile(src_abs, dest_abs):
                print("File is already in the static folder; skipping copy.")
                return dest_path
        except Exception:
            if src_abs == dest_abs:
                print("File is already in the static folder; skipping copy.")
                return dest_path
    try:
        shutil.copy2(src_path, dest_path)
        print(f"Copied file to {dest_path}")
    except shutil.SameFileError:
        print("SameFileError: file already exists in destination.")
    except Exception as e:
        print(f"Error copying file: {e}")
    return dest_path

# ----------------------------
#  Update Background Slot
# ----------------------------

@app.route("/admin/update_background", methods=["POST"])
def update_background():

    slot_number = request.form.get('slot_number')
    start_date_str = request.form.get('startDate')
    end_date_str = request.form.get('endDate')
    file = request.files.get('bgFile')
    
    if not slot_number:
        flash("Aucun slot n'a été sélectionné")
        return redirect(url_for('admin_background'))
    
    try:
        slot_number = int(slot_number)
        if slot_number < 1 or slot_number > 4:
            flash("Numéro de slot invalide")
            return redirect(url_for('admin_background'))
    except ValueError:
        flash("Numéro de slot invalide")
        return redirect(url_for('admin_background'))
    
    new_path = None
    if file:
        filename = file.filename
        static_dir = STATIC_IMAGES_DIR
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        save_path = os.path.join(static_dir, filename)
        file.save(save_path)
        new_path = os.path.join("./static/assets/images", filename).replace("\\", "/")
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
    except Exception:
        start_date = None
    try:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
    except Exception:
        end_date = None
    
    slots = parse_slots_from_css(CSS_FILE_PATH)
    idx = slot_number - 1
    if new_path:
        slots[idx]['path'] = new_path
    slots[idx]['start'] = start_date
    slots[idx]['end'] = end_date
    write_slots_to_css(CSS_FILE_PATH, slots)
    
    flash(f"Background du slot {slot_number} mis à jour avec succès!")
    return redirect(url_for('admin_background'))

@app.route("/admin/update_gtfs", methods=["POST"])
def admin_update_gtfs():
    transport = request.form.get("transport")
    uploaded = request.files.get("gtfs_zip")

    if not transport or not uploaded or uploaded.filename == "":
        flash("Aucun fichier sélectionné.", "danger")
        return redirect(url_for("admin_settings"))

    # Make sure it's a zip
    if not uploaded.filename.lower().endswith(".zip"):
        flash("Merci de télécharger un fichier ZIP GTFS.", "warning")
        return redirect(url_for("admin_settings"))

    # Save to a temp file
    tmp_path = os.path.join(os.getcwd(), uploaded.filename)
    uploaded.save(tmp_path)

    # Decide target folder
    if transport == "stm":
        target_dir = os.path.join(os.getcwd(), "STM")
    else:
        target_dir = os.path.join(os.getcwd(), "Exo", "Train")

    # Ensure folder exists
    os.makedirs(target_dir, exist_ok=True)

    # Extract
    try:
        with zipfile.ZipFile(tmp_path, "r") as z:
            z.extractall(target_dir)
    except Exception as e:
        flash(f"Erreur d'extraction : {e}", "danger")
        os.remove(tmp_path)
        return redirect(url_for("admin_settings"))
    finally:
        # Clean up the temp zip
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # Update JSON timestamp
    info = load_gtfs_update_info()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info[transport] = now
    save_gtfs_update_info(info)

    flash(f"Fichiers GTFS {transport.upper()} mis à jour avec succès ! ({now})", "success")
    return redirect(url_for("admin_settings"))

# ----------------------------
# This run the App
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
