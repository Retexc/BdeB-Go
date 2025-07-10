#!/usr/bin/env python3
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

# This file will store your custom alerts as an array of alert objects.
ALERT_FILE = "custom_messages.json"

# Global variable to track which alert is currently being edited.
editing_index = None

def load_alerts():
    if not os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    try:
        with open(ALERT_FILE, "r", encoding="utf-8") as f:
            alerts = json.load(f)
            if not isinstance(alerts, list):
                alerts = []
    except Exception as e:
        alerts = []
    return alerts

def save_alerts(alerts):
    with open(ALERT_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

def add_alert(header, description):
    alerts = load_alerts()
    alerts.append({
        "header": header,
        "description": description,
        "severity": "alert"  # same severity as other alerts in your Flask app
    })
    save_alerts(alerts)

def update_alert(index, header, description):
    alerts = load_alerts()
    if 0 <= index < len(alerts):
        alerts[index]["header"] = header
        alerts[index]["description"] = description
        save_alerts(alerts)

def remove_alert(index):
    alerts = load_alerts()
    if 0 <= index < len(alerts):
        alerts.pop(index)
        save_alerts(alerts)

def refresh_listbox(listbox):
    listbox.delete(0, tk.END)
    alerts = load_alerts()
    for i, alert in enumerate(alerts):
        # Display just the title and first 50 characters of description
        desc = alert.get("description", "")
        if len(desc) > 50:
            desc = desc[:50] + "..."
        listbox.insert(tk.END, f"{i+1}. {alert.get('header', 'No Title')}: {desc}")

def add_alert_callback(entry_title, text_desc, listbox):
    header = entry_title.get().strip()
    description = text_desc.get("1.0", "end").strip()
    if not header or not description:
        messagebox.showwarning("Avertissement", "Veuillez remplir le titre et la description.")
        return
    add_alert(header, description)
    messagebox.showinfo("Succès", "Message ajouté avec succès.")
    entry_title.delete(0, tk.END)
    text_desc.delete("1.0", tk.END)
    refresh_listbox(listbox)

def remove_selected_callback(listbox):
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un message à supprimer.")
        return
    index = selected[0]
    remove_alert(index)
    refresh_listbox(listbox)

def modify_selected_callback(listbox, entry_title, text_desc, btn_save_mod):
    global editing_index
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un message à modifier.")
        return
    editing_index = selected[0]
    alerts = load_alerts()
    alert = alerts[editing_index]
    # Populate the fields with current alert data.
    entry_title.delete(0, tk.END)
    entry_title.insert(0, alert.get("header", ""))
    text_desc.delete("1.0", tk.END)
    text_desc.insert("1.0", alert.get("description", ""))
    # Enable the save-modification button.
    btn_save_mod.config(state=tk.NORMAL)

def save_modification_callback(entry_title, text_desc, listbox, btn_save_mod):
    global editing_index
    if editing_index is None:
        messagebox.showwarning("Avertissement", "Aucun message n'est en cours de modification.")
        return
    header = entry_title.get().strip()
    description = text_desc.get("1.0", "end").strip()
    if not header or not description:
        messagebox.showwarning("Avertissement", "Veuillez remplir le titre et la description.")
        return
    update_alert(editing_index, header, description)
    messagebox.showinfo("Succès", "Message modifié avec succès.")
    # Clear the fields and reset editing index.
    entry_title.delete(0, tk.END)
    text_desc.delete("1.0", tk.END)
    editing_index = None
    btn_save_mod.config(state=tk.DISABLED)
    refresh_listbox(listbox)

def main():
    root = tk.Tk()
    root.title("Gestion des messages personnalisés")
    root.geometry("500x500")
    root.resizable(False, False)
    root.configure(bg="#e0f0ff")  # Light blue background

    # Configure ttk style for a modern look
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", background="#e0f0ff", font=("Helvetica", 12))
    style.configure("TEntry", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12, "bold"), foreground="#ffffff", background="#007acc")

    # Main container frame
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    lbl_current = ttk.Label(frame, text="Messages personnalisés actuels:")
    lbl_current.pack(anchor="w", pady=(10, 5))

    listbox = tk.Listbox(frame, height=10, font=("Helvetica", 12))
    listbox.pack(fill=tk.BOTH, expand=True, pady=5)
    refresh_listbox(listbox)

    lbl_title = ttk.Label(frame, text="Titre:")
    lbl_title.pack(anchor="w", pady=(10, 0))
    entry_title = ttk.Entry(frame, width=50)
    entry_title.pack(pady=5)

    lbl_desc = ttk.Label(frame, text="Description:")
    lbl_desc.pack(anchor="w", pady=(10, 0))
    text_desc = tk.Text(frame, width=50, height=4, font=("Helvetica", 12))
    text_desc.pack(pady=5)

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=10)
    
    btn_add = ttk.Button(btn_frame, text="Ajouter Message",
                         command=lambda: add_alert_callback(entry_title, text_desc, listbox))
    btn_add.pack(side=tk.LEFT, padx=5)
    
    btn_modify = ttk.Button(btn_frame, text="Modifier Message",
                            command=lambda: modify_selected_callback(listbox, entry_title, text_desc, btn_save_mod))
    btn_modify.pack(side=tk.LEFT, padx=5)
    
    btn_save_mod = ttk.Button(btn_frame, text="Enregistrer Modification", state=tk.DISABLED,
                            command=lambda: save_modification_callback(entry_title, text_desc, listbox, btn_save_mod))
    btn_save_mod.pack(side=tk.LEFT, padx=5)
    
    btn_remove = ttk.Button(btn_frame, text="Supprimer Message",
                            command=lambda: remove_selected_callback(listbox))
    btn_remove.pack(side=tk.LEFT, padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()
