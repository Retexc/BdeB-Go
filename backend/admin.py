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
import io
import tempfile
from datetime import datetime
from pathlib import Path

import logging
import requests
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
BASE_DIR = Path(__file__).resolve().parent  # /backend/
PROJECT_ROOT = BASE_DIR.parent               
INSTALL_DIR = PROJECT_ROOT                   
GITHUB_REPO = "https://github.com/Retexc/BdeB-Go.git"
GITHUB_API_REPO = "Retexc/BdeB-Go"

CSS_FILE_PATH = BASE_DIR / "static" / "index.css"
STATIC_IMAGES_DIR = BASE_DIR / "static" / "assets" / "images"
IMAGES_DIR = STATIC_IMAGES_DIR  

UPDATE_INFO_FILE = PROJECT_ROOT / "gtfs_update_info.json"
AUTO_UPDATE_CFG = INSTALL_DIR / "auto_update_config.json"

# Frontend paths
UI_DIR = PROJECT_ROOT / "UI"
UI_DIST_DIR = UI_DIR / "dist"
ADMIN_FRONTEND_DIR = PROJECT_ROOT / "admin-frontend"
ADMIN_DIST_DIR = ADMIN_FRONTEND_DIR / "dist"

# SPA dist path (for serving the admin interface)
SPA_DIST = ADMIN_DIST_DIR

STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

main_app_logs = []
app_process = None

# === Git utilities ===

def find_git_executable():
    """Find git executable on the system"""
    git_paths = [
        "git",  # If git is in PATH
        "C:/Program Files/Git/bin/git.exe",
        "C:/Program Files (x86)/Git/bin/git.exe", 
        "C:/Users/{}/AppData/Local/Programs/Git/bin/git.exe".format(os.getenv('USERNAME', '')),
        "C:/Git/bin/git.exe",
    ]
    
    for git_path in git_paths:
        if shutil.which(git_path) or (Path(git_path).exists() if git_path.endswith('.exe') else False):
            return git_path
    
    return None

def run_git_command(args, **kwargs):
    """Run a git command with proper error handling"""
    git_exe = find_git_executable()
    if not git_exe:
        raise Exception("Git not found. Please install Git and add it to your PATH.")
    
    cmd = [git_exe] + args
    return subprocess.run(cmd, **kwargs)

# === Update system functions ===

def get_remote_commit_sha():
    """Get the latest commit SHA from GitHub API"""
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_API_REPO}/commits/main"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        return response.json()["sha"]
    except Exception as e:
        logger.error(f"Failed to get remote commit: {e}")
        raise

def get_local_commit_sha():
    git_exe = find_git_executable()
    if git_exe:
        try:
            result = run_git_command(
                ["-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
    
    try:
        git_head = PROJECT_ROOT / ".git" / "HEAD"
        if git_head.exists():
            head_content = git_head.read_text().strip()
            if head_content.startswith("ref: "):
                # Read the ref file
                ref_path = PROJECT_ROOT / ".git" / head_content[5:]
                if ref_path.exists():
                    return ref_path.read_text().strip()
            else:
                # Direct SHA
                return head_content
    except:
        pass
    
    return None

def copy_directory_contents(src, dst):
    preserve_files = {
        "gtfs_update_info.json",
        "auto_update_config.json", 
        "backend/static/assets/images",  # User uploaded images
    }
    
    for src_file in src.rglob("*"):
        if src_file.is_file():
            rel_path = src_file.relative_to(src)
            dst_file = dst / rel_path
            should_preserve = any(str(rel_path).startswith(preserve) for preserve in preserve_files)  
            if should_preserve and dst_file.exists():
                logger.info(f"Preserving existing file: {rel_path}")
                continue
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)

def download_and_extract_update():
    try:
        zip_url = f"https://github.com/{GITHUB_API_REPO}/archive/refs/heads/main.zip"
        logger.info(f"Downloading update from {zip_url}")
        
        response = requests.get(zip_url, timeout=300)  # 5 minute timeout
        response.raise_for_status()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "update.zip"      
            zip_path.write_bytes(response.content)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                safe_extract(zip_file, temp_path)
            
            extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and d.name != "__pycache__"]
            if not extracted_dirs:
                raise Exception("No directories found in downloaded ZIP")        
            source_dir = extracted_dirs[0]
            backup_dir = PROJECT_ROOT.parent / f"BdeB-Go-backup-{int(time.time())}"
            logger.info(f"Creating backup at {backup_dir}")
            try:
                shutil.copytree(PROJECT_ROOT, backup_dir, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")
            logger.info("Copying new files...")
            copy_directory_contents(source_dir, PROJECT_ROOT)
            
            logger.info("Update completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Download and extract failed: {e}")
        raise

def perform_app_update_git():
    try:
        git_exe = find_git_executable()
        if not git_exe:
            raise Exception("Git not found. Please install Git and add it to your PATH.")
        git_dir = PROJECT_ROOT / ".git"
        if not git_dir.is_dir():
            logger.error(f"No git repository found at {PROJECT_ROOT}")
            raise Exception(f"Not a git repository: {PROJECT_ROOT}")        
        logger.info(f"Git repository found at {PROJECT_ROOT}, using git: {git_exe}")
        status_result = run_git_command(
            ["-C", str(PROJECT_ROOT), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if status_result.returncode != 0:
            raise Exception(f"Git status failed: {status_result.stderr}")
        
        if status_result.stdout.strip():
            logger.warning("Uncommitted changes detected, stashing them...")
            stash_result = run_git_command(
                ["-C", str(PROJECT_ROOT), "stash", "push", "-m", f"Auto-stash before update {datetime.now()}"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if stash_result.returncode != 0:
                logger.warning(f"Stash failed: {stash_result.stderr}")
        reset_result = run_git_command(
            ["-C", str(PROJECT_ROOT), "reset", "--hard", "HEAD"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if reset_result.returncode != 0:
            logger.warning(f"Reset failed: {reset_result.stderr}")
        logger.info("Fetching latest changes...")
        fetch_result = run_git_command(
            ["-C", str(PROJECT_ROOT), "fetch", "origin"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if fetch_result.returncode != 0:
            raise Exception(f"Git fetch failed: {fetch_result.stderr}")

        logger.info("Pulling changes...")
        pull_result = run_git_command(
            ["-C", str(PROJECT_ROOT), "pull", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if pull_result.returncode != 0:
            logger.info("Main branch failed, trying master...")
            pull_result = run_git_command(
                ["-C", str(PROJECT_ROOT), "pull", "origin", "master"],
                capture_output=True,
                text=True,
                timeout=300
            )
            if pull_result.returncode != 0:
                raise Exception(f"Git pull failed: {pull_result.stderr}")
        
        logger.info(f"Git pull successful: {pull_result.stdout}")
        return True
        
    except Exception as e:
        logger.error(f"Git update failed: {e}")
        raise

def perform_app_update_http():
    try:
        logger.info("Starting app update (Git-free method)")
        download_and_extract_update()
        return True
        
    except Exception as e:
        logger.error(f"HTTP update failed: {e}")
        raise

def perform_app_update():
    git_exe = find_git_executable()
    git_dir = PROJECT_ROOT / ".git"
    
    update_successful = False
    
    if git_exe and git_dir.exists():
        logger.info("Git available, using Git-based update")
        try:
            perform_app_update_git()
            update_successful = True
        except Exception as e:
            logger.warning(f"Git update failed: {e}, falling back to HTTP download")
    
    if not update_successful:
        logger.info("Using HTTP-based update (no Git required)")
        perform_app_update_http()
    
    try:
        # Update pip
        logger.info("Updating pip...")
        pip_result = subprocess.run(
            [PYTHON_EXEC, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True, text=True, timeout=300
        )
        if pip_result.returncode != 0:
            logger.warning(f"Pip upgrade failed: {pip_result.stderr}")

        # Install requirements 
        req = PROJECT_ROOT / "requirements.txt"
        if req.exists():
            logger.info("Installing requirements...")
            req_result = subprocess.run(
                [PYTHON_EXEC, "-m", "pip", "install", "-r", str(req)],
                capture_output=True, text=True, timeout=600
            )
            if req_result.returncode != 0:
                logger.warning(f"Requirements installation had issues: {req_result.stderr}")
        
        # Run install.bat 
        install_bat = PROJECT_ROOT / "install.bat"
        if install_bat.exists():
            logger.info("Running install.bat in silent mode to rebuild frontend...")
            try:
                install_result = subprocess.run(
                    [str(install_bat), "silent"], 
                    cwd=str(PROJECT_ROOT),
                    capture_output=True, text=True,
                    timeout=900, shell=True
                )
                
                if install_result.returncode == 0:
                    logger.info("install.bat completed successfully")
                else:
                    logger.warning(f"install.bat returned code {install_result.returncode}")
                    logger.warning(f"install.bat stderr: {install_result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error("install.bat timed out after 15 minutes")
                raise Exception("Frontend rebuild timed out")
            except Exception as e:
                logger.error(f"Error running install.bat: {e}")
                raise Exception(f"Frontend rebuild failed: {e}")
        else:
            logger.warning("install.bat not found, skipping frontend rebuild")
        
    except Exception as e:
        logger.error(f"Post-update steps failed: {e}")
        raise

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
    if not path_url:
        return None
    cleaned = path_url.lstrip("/")
    fs_path = BASE_DIR / cleaned  
    return fs_path

@app.route("/admin/backgrounds", methods=["GET"])
def api_get_backgrounds():
    slots = parse_slots_from_css_json(CSS_FILE_PATH)
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
    try:
        try:
            remote_sha = get_remote_commit_sha()
        except Exception as e:
            return jsonify({"error": f"Could not get remote commit: {e}"}), 500
        local_sha = get_local_commit_sha()
        
        if not local_sha:
            return jsonify({
                "error": "Could not determine local version",
                "up_to_date": False,
                "needs_update": True,
                "method": "api"
            }), 200
        
        up_to_date = local_sha == remote_sha
        
        return jsonify({
            "up_to_date": up_to_date,
            "local": local_sha[:8] if local_sha else "unknown",
            "remote": remote_sha[:8],
            "local_full": local_sha,
            "remote_full": remote_sha,
            "method": "api",
            "has_git": find_git_executable() is not None
        }), 200
        
    except Exception as e:
        logger.error("Error checking update: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/admin/app_update", methods=["POST"])
def admin_app_update():
    try:
        perform_app_update()
        message = f"Application mise à jour ! ({datetime.now():%Y-%m-%d %H:%M:%S})"
        
        # Return success with reload instruction
        return jsonify({
            "status": "success", 
            "message": message,
            "reload_required": True,
            "reload_delay": 3000  # 3 seconds delay
        }), 200
        
    except Exception as e:
        err_msg = f"Erreur lors de la mise à jour : {str(e)}"
        return jsonify({"status": "error", "message": err_msg}), 500

@app.route("/admin/debug/git_status", methods=["GET"])
def debug_git_status():
    """Debug route to check git repository status"""
    try:
        results = {}
        git_dir = PROJECT_ROOT / ".git"
        results["is_git_repo"] = git_dir.is_dir()
        results["project_root"] = str(PROJECT_ROOT)
        results["base_dir"] = str(BASE_DIR)
        results["git_dir_path"] = str(git_dir)
        
        if results["is_git_repo"]:
            git_exe = find_git_executable()
            if git_exe:
                # Get current branch
                try:
                    branch_result = run_git_command(
                        ["-C", str(PROJECT_ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
                        capture_output=True, text=True
                    )
                    results["current_branch"] = branch_result.stdout.strip() if branch_result.returncode == 0 else f"ERROR: {branch_result.stderr}"
                except Exception as e:
                    results["current_branch"] = f"ERROR: {e}"
                
                # Get current commit
                try:
                    commit_result = run_git_command(
                        ["-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
                        capture_output=True, text=True
                    )
                    results["current_commit"] = commit_result.stdout.strip() if commit_result.returncode == 0 else f"ERROR: {commit_result.stderr}"
                except Exception as e:
                    results["current_commit"] = f"ERROR: {e}"
                
                # Get repository status
                try:
                    status_result = run_git_command(
                        ["-C", str(PROJECT_ROOT), "status", "--porcelain"],
                        capture_output=True, text=True
                    )
                    results["uncommitted_changes"] = status_result.stdout.strip() if status_result.returncode == 0 else f"ERROR: {status_result.stderr}"
                except Exception as e:
                    results["uncommitted_changes"] = f"ERROR: {e}"
                
                # Get remote URL
                try:
                    remote_result = run_git_command(
                        ["-C", str(PROJECT_ROOT), "config", "--get", "remote.origin.url"],
                        capture_output=True, text=True
                    )
                    results["remote_url"] = remote_result.stdout.strip() if remote_result.returncode == 0 else f"ERROR: {remote_result.stderr}"
                except Exception as e:
                    results["remote_url"] = f"ERROR: {e}"
            else:
                results["git_available"] = False
                results["error"] = "Git executable not found"
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/debug/system_info", methods=["GET"])
def debug_system_info():
    try:
        info = {}
        
        # Check if git is in PATH
        git_exe = find_git_executable()
        info["git_executable"] = git_exe if git_exe else "NOT FOUND"
        
        # Check Python info
        info["python_executable"] = PYTHON_EXEC
        info["python_version"] = sys.version
        
        # Check paths
        info["project_root"] = str(PROJECT_ROOT)
        info["base_dir"] = str(BASE_DIR)
        info["is_git_repo"] = (PROJECT_ROOT / ".git").exists()
        
        # Check PATH environment
        path_env = os.environ.get('PATH', '')
        git_in_path = any('git' in p.lower() for p in path_env.split(os.pathsep))
        info["git_in_path"] = git_in_path
        
        common_git_paths = [
            "C:/Program Files/Git/bin/git.exe",
            "C:/Program Files (x86)/Git/bin/git.exe",
        ]
        existing_git_paths = [p for p in common_git_paths if Path(p).exists()]
        info["existing_git_installations"] = existing_git_paths
        

        try:
            import requests
            info["requests_available"] = True
            info["requests_version"] = requests.__version__
        except ImportError:
            info["requests_available"] = False
        
        return jsonify(info), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        if tmp_zip.exists():
            try:
                tmp_zip.unlink()
            except:
                pass
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
                    local_sha = get_local_commit_sha()
                    remote_sha = get_remote_commit_sha()
                    
                    if local_sha and remote_sha and local_sha != remote_sha:
                        logger.info("Auto-update: new commit detected, updating...")
                        perform_app_update()
                    elif not local_sha:
                        logger.warning("Auto-update: Could not determine local version")
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

def auto_start_main_app():
    """Auto-start the main app when admin server starts"""
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true' and os.getenv("FLASK_ENV") == "development":
        return
    def delayed_start():
        time.sleep(5)
        
        if app.config["APP_RUNNING"]:
            logger.info("Main application is already running, skipping auto-start")
            return
        try:
            logger.info("Auto-starting main application...")
            with app.app_context():
                result = admin_start()
                data, status_code = result
                if status_code == 200:
                    response_data = data.get_json()
                    if response_data.get("status") == "started":
                        logger.info("✅ BdeB-Go has started successfully!")
                        time.sleep(3)
                    elif response_data.get("status") == "already_running":
                        logger.info("✅ BdeB-Go was already running")
                else:
                    logger.error("❌ Failed to auto-start BdeB-Go")
        except Exception as e:
            logger.error("❌ Error auto-starting BdeB-Go: %s", e)
            main_app_logs.append(f"{datetime.now()} - Auto-start failed: {e}")
    
    threading.Thread(target=delayed_start, daemon=True).start()

auto_start_main_app()  

if __name__ == "__main__":
    if os.getenv("FLASK_ENV") == "development":
        app.run(debug=True, use_reloader=True, host="127.0.0.1", port=5001)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5001, threads=8)