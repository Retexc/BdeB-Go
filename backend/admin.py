#!/usr/bin/env python
import sys
import os
import subprocess
import threading
import json
import zipfile
import shutil
import time
import re
from datetime import datetime
from pathlib import Path

import logging
from flask import (
    Flask,
    jsonify,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app,
)
from werkzeug.utils import secure_filename
from flask_cors import CORS
from .managers.background_manager import get_slots, set_slots, list_images


print(f"[DEBUG] Running admin.py from {Path(__file__).resolve()}")

if getattr(sys, "_MEIPASS", None):
    # PyInstaller onefile puts extracted files here
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.secret_key = "replace-with-your-secure-secret-key"
app.config["APP_RUNNING"] = False
logger = app.logger
logger.setLevel(logging.INFO)
CORS(app)

# === Constants / paths ===
PYTHON_EXEC = sys.executable
BASE_DIR = Path(__file__).resolve().parent  
PROJECT_ROOT = BASE_DIR.parent   
INSTALL_DIR = BASE_DIR  
GITHUB_REPO = "https://github.com/Retexc/BdeB-Go.git"

CSS_FILE_PATH = BASE_DIR / "static" / "index.css"
STATIC_IMAGES_DIR = BASE_DIR / "static" / "assets" / "images"
IMAGES_DIR = STATIC_IMAGES_DIR  

UPDATE_INFO_FILE = PROJECT_ROOT / "gtfs_update_info.json"
AUTO_UPDATE_CFG = INSTALL_DIR / "auto_update_config.json"

SPA_DIST = Path(__file__).resolve().parent / ".." / "admin-frontend" / "dist"

STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

main_app_logs = []
app_process = None

# === Helpers for MULTISLOT JSON format ===


def parse_slots_from_css_json(css_path: Path):
    if not css_path.exists():
        return []
    try:
        content = css_path.read_text(encoding="utf-8")
    except Exception:
        return []
    m = re.search(r"/\*\s*MULTISLOT:\s*(\[\s*[\s\S]*?\])\s*\*/", content, re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    try:
        return json.loads(m.group(1))
    except Exception:
        return []


def write_slots_to_css_json(css_path: Path, slots):
    block = "/* MULTISLOT:\n" + json.dumps(slots, indent=2) + "\n*/"
    if not css_path.exists():
        css_path.write_text(block + "\n", encoding="utf-8")
        return
    content = css_path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"/\*\s*MULTISLOT:\s*\[[\s\S]*?\]\s*\*/",
        block,
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count:
        css_path.write_text(updated, encoding="utf-8")
    else:
        # append if missing
        with open(css_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + block + "\n")


def safe_extract(zipf: zipfile.ZipFile, dest: Path):
    dest = dest.resolve()
    for member in zipf.namelist():
        member_path = dest / member
        resolved = member_path.resolve()
        if not str(resolved).startswith(str(dest)):
            raise RuntimeError("Unsafe path in zip file")
    zipf.extractall(dest)


def capture_app_logs(process):
    """Continuously read stdout from the main app process."""
    while True:
        line = process.stdout.readline()
        if not line:
            break
        main_app_logs.append(line.rstrip())
    app.config["APP_RUNNING"] = False
    logger.info("Main app process ended.")


# ----- Persistence helpers -----


def load_auto_update_cfg():
    default = {"enabled": True, "time": "20:00"}
    if AUTO_UPDATE_CFG.exists():
        try:
            with open(AUTO_UPDATE_CFG, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                default.update(cfg)
        except:
            pass
    return default


def save_auto_update_cfg(cfg):
    with open(AUTO_UPDATE_CFG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def load_gtfs_update_info():
    if UPDATE_INFO_FILE.exists():
        try:
            with open(UPDATE_INFO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"stm": None, "exo": None}


def save_gtfs_update_info(info):
    try:
        with open(UPDATE_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
    except Exception as e:
        logger.error("Error saving GTFS info: %s", e)


# ----- Routes -----


@app.route("/admin/ping", methods=["GET"])
def ping():
    return jsonify({"pong": True}), 200

def path_url_to_fs(path_url: str) -> Path | None:
    # Expecting something like "/static/assets/images/foo.jpg"
    if not path_url:
        return None
    # strip leading slash
    cleaned = path_url.lstrip("/")
    fs_path = BASE_DIR / cleaned  # BASE_DIR is the repo's path to admin backend
    return fs_path

@app.route("/admin/backgrounds", methods=["GET"])
def api_get_backgrounds():
    slots = parse_slots_from_css_json(CSS_FILE_PATH)
    # sanitize: if a slot points to an image that was deleted, drop it
    for s in slots:
        p = s.get("path")
        if p:
            fs = path_url_to_fs(p)
            if not fs or not fs.exists():
                s["path"] = None
    return jsonify(slots), 200


@app.route("/admin/backgrounds", methods=["POST"])
def api_set_backgrounds():
    payload = request.get_json() or {}
    slots = payload.get("slots", [])
    write_slots_to_css_json(CSS_FILE_PATH, slots)
    return jsonify({"status": "success"}), 200


@app.route("/admin/backgrounds/images", methods=["GET"])
def api_list_images():
    return jsonify(list_images()), 200


@app.route("/admin/update_background", methods=["POST"])
def update_background():
    slot_num = request.form.get("slot_number")
    start_str = request.form.get("startDate")
    end_str = request.form.get("endDate")
    file = request.files.get("bgFile")

    if not slot_num:
        flash("Aucun slot n'a été sélectionné", "warning")
        return redirect(url_for("serve_spa", path=""))

    try:
        idx = int(slot_num) - 1
        if idx not in range(4):
            raise ValueError()
    except:
        flash("Numéro de slot invalide", "danger")
        return redirect(url_for("serve_spa", path=""))

    slots = parse_slots_from_css_json(CSS_FILE_PATH)
    # Ensure at least 4 slots
    while len(slots) < 4:
        slots.append({"path": None, "start": None, "end": None})

    if file and file.filename:
        os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)
        save_path = STATIC_IMAGES_DIR / secure_filename(file.filename)
        file.save(save_path)
        new_path = url_for("static", filename=f"assets/images/{file.filename}")
        slots[idx]["path"] = new_path

    try:
        if start_str:
            slots[idx]["start"] = datetime.strptime(start_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        pass
    try:
        if end_str:
            slots[idx]["end"] = datetime.strptime(end_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        pass

    write_slots_to_css_json(CSS_FILE_PATH, slots)
    flash(f"Background du slot {idx+1} mis à jour avec succès !", "success")
    return redirect(url_for("serve_spa", path=""))


@app.route("/admin/backgrounds/import", methods=["POST"])
def api_import_background():
    if "image" not in request.files:
        return jsonify({"error": "no file part"}), 400
    f = request.files["image"]
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400

    filename = secure_filename(f.filename)
    dest = STATIC_IMAGES_DIR / filename

    try:
        f.save(dest)
    except Exception as e:
        return jsonify({"error": f"could not save: {e}"}), 500

    url = f"/static/assets/images/{filename}"

    slots = parse_slots_from_css_json(CSS_FILE_PATH)
    new_slot = {
        "path": url,
        "start": datetime.now().strftime("%Y-%m-%d"),
        "end": None,
    }
    slots = [s for s in slots if s.get("path") != url]
    slots.insert(0, new_slot)
    if len(slots) > 4:
        slots = slots[:4]
    write_slots_to_css_json(CSS_FILE_PATH, slots)

    return jsonify({"status": "success", "url": url, "slots": slots}), 200

@app.route("/admin/check_update", methods=["GET"])
def admin_check_update():
    """
    Compare local HEAD to remote HEAD. Return whether an update is available.
    """
    try:
        # Get local commit
        local = subprocess.check_output(
            ["git", "-C", INSTALL_DIR, "rev-parse", "HEAD"],
            universal_newlines=True
        ).strip()

        # Get remote HEAD (without using shell=True for safety)
        remote_output = subprocess.check_output(
            ["git", "ls-remote", GITHUB_REPO, "HEAD"],
            universal_newlines=True
        ).strip()
        remote = remote_output.split()[0] if remote_output else None

        if not remote:
            return jsonify(error="could not get remote HEAD"), 500

        up_to_date = local == remote

        return jsonify({
            "up_to_date": up_to_date,
            "local": local,
            "remote": remote,
        }), 200
    except Exception as e:
        logger.error("Error checking update: %s", e)
        return jsonify(error=str(e)), 500
    
def perform_app_update():
    if (INSTALL_DIR / ".git").is_dir():
        subprocess.check_call(["git", "-C", str(INSTALL_DIR), "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    else:
        subprocess.check_call(["git", "clone", GITHUB_REPO, str(INSTALL_DIR)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    subprocess.check_call([PYTHON_EXEC, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    req = INSTALL_DIR / "requirements.txt"
    if req.exists():
        subprocess.check_call([PYTHON_EXEC, "-m", "pip", "install", "-r", str(req)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


@app.route("/admin/app_update", methods=["POST"])
def admin_app_update():
    try:
        perform_app_update()
        message = f"Application mise à jour ! ({datetime.now():%Y-%m-%d %H:%M:%S})"
        # return JSON instead of redirect
        return jsonify({"status": "success", "message": message}), 200
    except subprocess.CalledProcessError as e:
        err_msg = f"Erreur lors de la mise à jour : {e}"
        return jsonify({"status": "error", "message": err_msg}), 500



@app.route("/admin/auto_update_settings", methods=["POST"])
def auto_update_settings():
    enabled = bool(request.form.get("enabled"))
    time_str = request.form.get("time", "20:00")
    cfg = {"enabled": enabled, "time": time_str}
    save_auto_update_cfg(cfg)
    flash("Paramètres de mise à jour automatique enregistrés", "success")
    return redirect(url_for("serve_spa", path=""))


@app.route("/admin/update_gtfs", methods=["POST"])
def admin_update_gtfs():
    transport = request.form.get("transport", "").lower()
    z = request.files.get("gtfs_zip")

    if transport not in ("stm", "exo"):
        flash("Transport invalide.", "danger")
        return redirect(url_for("serve_spa", path=""))

    if not z or z.filename == "":
        flash("Aucun fichier sélectionné.", "danger")
        return redirect(url_for("serve_spa", path=""))

    if not z.filename.lower().endswith(".zip"):
        flash("Merci de télécharger un fichier ZIP GTFS.", "warning")
        return redirect(url_for("serve_spa", path=""))

    GTFS_ROOT = PROJECT_ROOT / "backend" / "GTFS"
    stm_dir = GTFS_ROOT / "stm"
    exo_dir = GTFS_ROOT / "exo"

    # Decide target
    if transport == "stm":
        target = stm_dir
    else:
        target = exo_dir / "Train"

    timestamp = int(time.time())
    tmp_zip = GTFS_ROOT / f"{transport}_uploaded_{timestamp}.zip"
    staging = GTFS_ROOT / f".tmp_extract_{transport}_{timestamp}"

    try:
        z.save(tmp_zip)

        with zipfile.ZipFile(tmp_zip, "r") as archive:
            safe_extract(archive, staging)

        entries = list(staging.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            extracted_root = entries[0]
        else:
            extracted_root = staging

        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(extracted_root), str(target))

        if staging.exists():
            try:
                shutil.rmtree(staging)
            except:
                pass

        # Record update time
        info = load_gtfs_update_info()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info[transport] = now
        save_gtfs_update_info(info)

        flash(f"Fichiers GTFS {transport.upper()} mis à jour avec succès ! ({now})", "success")
    except Exception as e:
        logger.exception("GTFS update failed")
        flash(f"Erreur d'extraction ou de mise à jour : {e}", "danger")
    finally:
        # Cleanup temp zip
        if tmp_zip.exists():
            try:
                tmp_zip.unlink()
            except:
                pass
        # Cleanup leftover staging if any
        if staging.exists():
            try:
                shutil.rmtree(staging)
            except:
                pass

    return redirect(url_for("serve_spa", path=""))

@app.route("/admin/gtfs_update_info", methods=["GET"])
def get_gtfs_update_info():
    info = load_gtfs_update_info()
    return jsonify(info), 200


@app.route("/admin/start", methods=["POST"])
def admin_start():
    global app_process
    if not app.config["APP_RUNNING"]:
        try:
            cmd = [
                PYTHON_EXEC,
                "-u",
                "-m",
                "waitress",
                "--threads=8",
                "--host=127.0.0.1",
                "--port=5000",
                "backend.main:app",
            ]
            app_process = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT), 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            app.config["APP_RUNNING"] = True
            main_app_logs.append(f"{datetime.now()} - Main app started.")
            threading.Thread(target=capture_app_logs, args=(app_process,), daemon=True).start()
            return jsonify({"status": "started"}), 200
        except Exception as e:
            logger.error("Error starting main app: %s", e)
            return jsonify({"status": "error", "error": str(e)}), 500
    return jsonify({"status": "already_running"}), 200


@app.route("/admin/stop", methods=["POST"])
def admin_stop():
    global app_process
    if app.config["APP_RUNNING"] and app_process:
        try:
            app_process.terminate()
            app_process.wait(timeout=10)
            app.config["APP_RUNNING"] = False
            main_app_logs.append(f"{datetime.now()} - Main app stopped.")
            return jsonify({"status": "stopped"}), 200
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 500
    return jsonify({"status": "not_running"}), 200


@app.route("/admin/status")
def admin_status():
    return jsonify({"running": app.config["APP_RUNNING"]})


@app.route("/admin/logs_data")
def logs_data():
    return "\n".join(main_app_logs)


def auto_update_worker():
    while True:
        cfg = load_auto_update_cfg()
        if cfg.get("enabled"):
            now = datetime.now()
            cutoff = datetime.strptime(cfg["time"], "%H:%M").time()
            if now.time() >= cutoff:
                try:
                    local = subprocess.check_output(
                        ["git", "-C", str(INSTALL_DIR), "rev-parse", "HEAD"], universal_newlines=True
                    ).strip()
                    remote = (
                        subprocess.check_output(["git", "ls-remote", GITHUB_REPO, "HEAD"], shell=True, universal_newlines=True)
                        .split()[0]
                    )
                    if local != remote:
                        logger.info("Auto-update: new commit detected, pulling…")
                        perform_app_update()
                except Exception as e:
                    logger.error("Auto-update error: %s", e)
        time.sleep(3600)


threading.Thread(target=auto_update_worker, daemon=True).start()


@app.route("/admin/", defaults={"path": ""})
@app.route("/admin/<path:path>")
def serve_spa(path):
    full_path = SPA_DIST / path
    if path and full_path.exists():
        return send_from_directory(str(SPA_DIST), path)
    return send_from_directory(str(SPA_DIST), "index.html")


if __name__ == "__main__":
    if os.getenv("FLASK_ENV") == "development":
        app.run(debug=True, use_reloader=True, host="127.0.0.1", port=5001)
    else:
        from waitress import serve

        serve(app, host="0.0.0.0", port=5001, threads=8)
