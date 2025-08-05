# background_manager.py
import os, shutil, json
from datetime import datetime

BASE_DIR    = os.path.dirname(__file__)            # .../src/bdeb_gtfs/managers
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))  # .../src/bdeb_gtfs

CSS_FILE     = os.path.join(PROJECT_DIR, 'static', 'index.css')
IMAGES_DIR   = os.path.join(PROJECT_DIR, 'static', 'assets', 'images')

def get_slots():
    """
    Read CSS_FILE, parse the MULTISLOT comment block,
    and return a list of slot dicts:
      [{ "path": "./assets/images/foo.png",
         "start": "2025-07-01",
         "end":   "2025-07-31" }, …]
    """
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    # find between /* MULTISLOT:  …  */
    start_token = '/* MULTISLOT:'
    start = text.find(start_token)
    if start == -1:
        # No MULTISLOT block present
        return []
    end = text.find('*/', start)
    if end == -1:
        # Unterminated block
        return []

    raw = text[start + len(start_token):end].strip()
    if not raw:
        # Empty block
        return []

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Invalid JSON inside the block
        return []

def set_slots(slots):
    """
    Given a list of slot dicts, copy any .path file
    into IMAGES_DIR, rewrite CSS_FILE’s MULTISLOT block.
    """
    # ensure images dir exists
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # maybe slots come in with local file paths (e.g. "C:\…\.png")
    for slot in slots:
        src = slot.get("path")
        if src and os.path.isfile(src):
            dst = shutil.copy(src, IMAGES_DIR)
            # normalize to relative web path
            slot["path"] = "./assets/images/" + os.path.basename(dst)

    # rebuild the CSS comment
    comment = "/* MULTISLOT:\n" + json.dumps(slots, indent=2) + "\n*/"
    # insert into the CSS template
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        parts = f.read().split('/* MULTISLOT:')
    new_css = parts[0] + comment + parts[1].split('*/',1)[1]
    with open(CSS_FILE, 'w', encoding='utf-8') as f:
        f.write(new_css)

def list_images():
    """
    Return all image file paths in IMAGES_DIR, newest first.
    Each entry is a web-relative path like './assets/images/foo.png'.
    """
    # ensure the folder is there
    os.makedirs(IMAGES_DIR, exist_ok=True)

    entries = []
    for e in os.scandir(IMAGES_DIR):
        if e.is_file():
            entries.append((e.stat().st_mtime, e.name))

    # sort newest first
    entries.sort(reverse=True)
    return [f"./assets/images/{name}" for _, name in entries]
