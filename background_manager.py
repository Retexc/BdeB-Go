import tkinter as tk
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry  # pip install tkcalendar
import datetime
import re
import os
import json
import shutil
from PIL import Image, ImageTk  # pip install pillow
import zipfile
from tkinter import ttk

# Paths for CSS and static images (used by the background manager)
CSS_FILE_PATH = "./static/index.css"
STATIC_IMAGES_DIR = "./static/assets/images"
UPDATE_INFO_FILE = "./gtfs_update_info.json"

def load_gtfs_update_info():
    """Load the last update times from a JSON file."""
    if os.path.exists(UPDATE_INFO_FILE):
        try:
            with open(UPDATE_INFO_FILE, "r", encoding="utf-8") as f:
                info = json.load(f)
            return info
        except Exception as e:
            print("Erreur lors du chargement des infos de mise à jour :", e)
    # Return default info if file doesn't exist or error occurs
    return {"stm": None, "exo": None}

def save_gtfs_update_info(info):
    """Save the update times dictionary to a JSON file."""
    try:
        with open(UPDATE_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
    except Exception as e:
        print("Erreur lors de l'enregistrement des infos de mise à jour :", e)

#############################################
# Existing functions for Background Manager #
#############################################

SLOT_COMMENT_HEADER = "/* MULTISLOT:"
SLOT_COMMENT_FOOTER = "*/"

def parse_slots_from_css(css_path):
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
    line_pattern = re.compile(r"SLOT(\d+):\s+(.+?)\s+from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
    for line in block_text.splitlines():
        line = line.strip()
        m = line_pattern.search(line)
        if m:
            slot_index = int(m.group(1))
            slot_path = m.group(2).strip()
            start_str = m.group(3)
            end_str = m.group(4)
            try:
                start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
            except ValueError:
                start_date = None
            try:
                end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
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
    if not os.path.isfile(css_path):
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(f"/* {block_text} */\n")
        return
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    pattern_block = re.compile(r"/\*\s*MULTISLOT:.*?\*/", re.IGNORECASE | re.DOTALL)
    new_block = f"/* {block_text} */"
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
        except:
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

class MultiSlotManagerApp:
    def __init__(self, parent):
        self.root = parent
        # Do not set title here if parent isn't the root
        self.slots_data = parse_slots_from_css(CSS_FILE_PATH)
        self.slot_frames = []
        for i in range(4):
            frame = self.build_slot_frame(i)
            frame.pack(padx=10, pady=10, fill="x")
            self.slot_frames.append(frame)
        tk.Button(self.root, text="Save All", command=self.on_save_all).pack(pady=10)

    def build_slot_frame(self, index):
        slot_frame = tk.LabelFrame(self.root, text=f"Slot {index+1}")
        slot_data = self.slots_data[index]
        path_var = tk.StringVar()
        if slot_data["path"]:
            path_var.set(slot_data["path"])
        start_var = DateEntry(slot_frame, date_pattern="yyyy-mm-dd")
        end_var = DateEntry(slot_frame, date_pattern="yyyy-mm-dd")
        if slot_data["start"]:
            start_var.set_date(slot_data["start"])
        if slot_data["end"]:
            end_var.set_date(slot_data["end"])
        preview_frame = tk.Frame(slot_frame, width=100, height=100, bg="#ddd")
        preview_frame.grid_propagate(False)
        preview_label = tk.Label(preview_frame, text="No image")
        preview_label.pack(expand=True, fill="both")
        if slot_data["path"] and os.path.isfile(slot_data["path"]):
            self.show_preview(slot_data["path"], preview_label)
        slot_frame.path_var = path_var
        slot_frame.start_var = start_var
        slot_frame.end_var = end_var
        slot_frame.preview_label = preview_label
        def on_browse():
            file_path = filedialog.askopenfilename(
                title="Select Background Image",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.webp"), ("All Files", "*.*")]
            )
            if file_path:
                path_var.set(file_path)
                self.show_preview(file_path, preview_label)
        row = 0
        tk.Label(slot_frame, text="Background File:").grid(row=row, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(slot_frame, textvariable=path_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        tk.Button(slot_frame, text="Browse...", command=on_browse).grid(row=row, column=2, padx=5, pady=5)
        row += 1
        tk.Label(slot_frame, text="Preview:").grid(row=row, column=0, padx=5, pady=5, sticky="e")
        preview_frame.grid(row=row, column=1, columnspan=2, padx=5, pady=5)
        row += 1
        tk.Label(slot_frame, text="Start Date:").grid(row=row, column=0, padx=5, pady=5, sticky="e")
        start_var.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        row += 1
        tk.Label(slot_frame, text="End Date:").grid(row=row, column=0, padx=5, pady=5, sticky="e")
        end_var.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        return slot_frame

    def show_preview(self, file_path, label_widget):
        try:
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            preview_img = ImageTk.PhotoImage(img)
            label_widget.config(image=preview_img, text="")
            label_widget.image = preview_img
        except Exception as e:
            label_widget.config(text="Error preview")

    def on_save_all(self):
        new_slots = []
        for i, frame in enumerate(self.slot_frames):
            path_str = frame.path_var.get().strip()
            final_path = None
            if path_str:
                final_path = copy_to_static_folder(path_str)
                if final_path and "static" in final_path.lower():
                    idx = final_path.lower().find("static")
                    if idx != -1:
                        final_path = "./" + final_path[idx:].replace("\\", "/")
            start_date = frame.start_var.get_date()
            end_date = frame.end_var.get_date()
            new_slots.append({
                "path": final_path,
                "start": start_date,
                "end": end_date
            })
        write_slots_to_css(CSS_FILE_PATH, new_slots)
        messagebox.showinfo("Saved", "All 4 slots have been saved to the CSS comment block.")

#############################################
# New: GTFS Manager Tab
#############################################

import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import webbrowser

class GTFSManagerApp:
    def __init__(self, parent):
        self.parent = parent
        # Load previously saved update info and store it
        self.update_info = load_gtfs_update_info()
        self.build_ui()

    def build_ui(self):
        message = (
            "Veuillez mettre à jour les fichiers GTFS lorsque cela est nécessaire.\n\n"
            "Les fichiers GTFS contiennent les horaires et les informations des autobus et des trains Exo. "
            "Il est nécessaire de les mettre à jour régulièrement.\n\n"
            "Vous pouvez utiliser les dates disponibles sur le site de la STM comme référence pour mettre à jour les fichiers.\n\n"
            "Pour télécharger les dernières versions des données GTFS, veuillez consulter les pages officielles suivantes :"
        )
        tk.Label(self.parent, text=message, font=("Helvetica", 14), justify="left", wraplength=600).pack(pady=10)

        # STM clickable link with icon (image shown under the text)
        stm_url = "https://www.stm.info/fr/a-propos/developpeurs"
        stm_icon_path = "./static/assets/images/STM_Web.png"  # adjust path as needed
        stm_icon = Image.open(stm_icon_path)
        stm_icon = stm_icon.resize((662, 315), Image.Resampling.LANCZOS)
        stm_icon_photo = ImageTk.PhotoImage(stm_icon)
        stm_label = tk.Label(
            self.parent,
            text=f"STM : {stm_url}",
            image=stm_icon_photo,
            compound="bottom",
            fg="blue",
            cursor="hand2",
            font=("Helvetica", 12, "underline"),
            justify="center",
            wraplength=600
        )
        stm_label.image = stm_icon_photo
        stm_label.pack(pady=2)
        stm_label.bind("<Button-1>", lambda event: webbrowser.open_new_tab(stm_url))

        # EXO clickable link with icon (image shown under the text)
        exo_url = "https://exo.quebec/fr/a-propos/donnees-ouvertes"
        exo_icon_path = "./static/assets/images/Exo_Web.png"  # adjust path as needed
        exo_icon = Image.open(exo_icon_path)
        exo_icon = exo_icon.resize((917, 51), Image.Resampling.LANCZOS)
        exo_icon_photo = ImageTk.PhotoImage(exo_icon)
        exo_label = tk.Label(
            self.parent,
            text=f"EXO : {exo_url}",
            image=exo_icon_photo,
            compound="bottom",
            fg="blue",
            cursor="hand2",
            font=("Helvetica", 12, "underline"),
            justify="center",
            wraplength=600
        )
        exo_label.image = exo_icon_photo
        exo_label.pack(pady=2)
        exo_label.bind("<Button-1>", lambda event: webbrowser.open_new_tab(exo_url))

        # GTFS file selection UI
        self.stm_var = tk.StringVar()
        self.exo_var = tk.StringVar()

        stm_frame = tk.LabelFrame(self.parent, text="GTFS STM")
        stm_frame.pack(padx=10, pady=10, fill="x")
        tk.Label(stm_frame, text="Fichier GTFS (ZIP):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(stm_frame, textvariable=self.stm_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(stm_frame, text="Browse...", command=self.browse_stm).grid(row=0, column=2, padx=5, pady=5)
        # Dernière mise à jour label for STM
        stm_update = self.update_info.get("stm") or "N/A"
        self.stm_update_label = tk.Label(stm_frame, text="Dernière mise à jour : " + stm_update, font=("Helvetica", 10))
        self.stm_update_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        exo_frame = tk.LabelFrame(self.parent, text="GTFS EXO")
        exo_frame.pack(padx=10, pady=10, fill="x")
        tk.Label(exo_frame, text="Fichier GTFS (ZIP):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(exo_frame, textvariable=self.exo_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(exo_frame, text="Browse...", command=self.browse_exo).grid(row=0, column=2, padx=5, pady=5)
        # Dernière mise à jour label for EXO
        exo_update = self.update_info.get("exo") or "N/A"
        self.exo_update_label = tk.Label(exo_frame, text="Dernière mise à jour : " + exo_update, font=("Helvetica", 10))
        self.exo_update_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Button(self.parent, text="Update GTFS", command=self.update_gtfs).pack(pady=10)

    def browse_stm(self):
        file_path = filedialog.askopenfilename(
            title="Select GTFS ZIP for STM",
            filetypes=[("ZIP Files", "*.zip"), ("All Files", "*.*")]
        )
        if file_path:
            self.stm_var.set(file_path)

    def browse_exo(self):
        file_path = filedialog.askopenfilename(
            title="Select GTFS ZIP for EXO",
            filetypes=[("ZIP Files", "*.zip"), ("All Files", "*.*")]
        )
        if file_path:
            self.exo_var.set(file_path)

    def update_gtfs(self):
        stm_zip = self.stm_var.get().strip()
        exo_zip = self.exo_var.get().strip()
        errors = []
        updated_stm = False
        updated_exo = False

        if stm_zip:
            try:
                with zipfile.ZipFile(stm_zip, "r") as zip_ref:
                    target_dir = "./STM"
                    zip_ref.extractall(target_dir)
                updated_stm = True
            except Exception as e:
                errors.append(f"STM: {e}")

        if exo_zip:
            try:
                with zipfile.ZipFile(exo_zip, "r") as zip_ref:
                    target_dir = "./Exo/Train"
                    zip_ref.extractall(target_dir)
                updated_exo = True
            except Exception as e:
                errors.append(f"EXO: {e}")

        if not stm_zip and not exo_zip:
            messagebox.showerror("Error", "Aucun fichier STM ou EXO sélectionné")
            return

        if errors:
            messagebox.showerror("Error", "\n".join(errors))
        else:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if updated_stm:
                self.stm_update_label.config(text="Dernière mise à jour : " + now_str)
                self.update_info["stm"] = now_str
            if updated_exo:
                self.exo_update_label.config(text="Dernière mise à jour : " + now_str)
                self.update_info["exo"] = now_str
            save_gtfs_update_info(self.update_info)
            messagebox.showinfo("Success", "Les fichiers GTFS ont été mis à jour avec succès!")



#############################################
# Main: Notebook with two tabs: Background & GTFS
#############################################

def main():
    root = tk.Tk()
    root.title("Multi-Slot Manager & GTFS Updater")
    root.iconbitmap("./static/assets/icons/icon.ico")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    background_tab = tk.Frame(notebook)
    gtfs_tab = tk.Frame(notebook)

    notebook.add(background_tab, text="Background")
    notebook.add(gtfs_tab, text="GTFS")

    # You can choose to wrap the background tab in a scrollable frame if needed.
    bg_app = MultiSlotManagerApp(background_tab)
    gtfs_app = GTFSManagerApp(gtfs_tab)

    root.mainloop()

if __name__ == "__main__":
    main()