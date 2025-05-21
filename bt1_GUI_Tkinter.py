import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os, json
import bt1module

CONFIG_FILE = ".bt1config.json"

# Load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"password": "test1", "salt": "", "dark_mode": False}

# Save configuration to file
def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(global_config, f)

# ==== Initial Config ====
global_config = load_config()

# ==== Dark Mode Handling ====
def apply_theme():
    style = ttk.Style()
    style.theme_use('default')
    if global_config['dark_mode']:
        root.configure(bg="#2e2e2e")
        style.configure("TLabel", background="#2e2e2e", foreground="white")
        style.configure("TButton", background="#444444", foreground="white")
        style.configure("TEntry", fieldbackground="#3a3a3a", foreground="white")
        style.map("TButton", background=[("active", "#555555")])
    else:
        root.configure(bg="lightgray")
        style.configure("TLabel", background="lightgray", foreground="black")
        style.configure("TButton", background="white", foreground="black")
        style.configure("TEntry", fieldbackground="white", foreground="black")
        style.map("TButton", background=[("active", "#e6e6e6")])

# ==== Helper Functions ====
def pick_file(entry):
    path = filedialog.askopenfilename()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def pick_output_file(entry):
    path = filedialog.asksaveasfilename(defaultextension=".bt1", filetypes=[("BT1 Files", "*.bt1")])
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def pick_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def get_salt():
    salt_hex = global_config.get("salt", "")
    try:
        return bytes.fromhex(salt_hex) if salt_hex else None
    except:
        messagebox.showerror("Salt Error", "Invalid salt (must be hex format)")
        return None

# ==== Pack and Unpack Functions ====
def pack_file():
    in_path = entry_pack_input.get()
    out_path = entry_pack_output.get()
    if not os.path.isfile(in_path):
        return messagebox.showerror("Error", "Input file does not exist")
    try:
        bt1module.bt1_pack_file(in_path, out_path, global_config['password'])
        messagebox.showinfo("Done", f"Packed: {out_path}")
    except Exception as e:
        messagebox.showerror("Packing Error", str(e))

def unpack_file():
    in_path = entry_unpack_input.get()
    out_dir = entry_unpack_output.get()
    if not os.path.isfile(in_path):
        return messagebox.showerror("Error", "Input file does not exist")
    if not os.path.isdir(out_dir):
        return messagebox.showerror("Error", "Invalid output directory")
    try:
        bt1module.bt1_unpack_file(in_path, out_dir, global_config['password'])
        messagebox.showinfo("Done", f"Unpacked to: {out_dir}")
    except Exception as e:
        messagebox.showerror("Unpacking Error", str(e))

# ==== GUI Setup ====
root = tk.Tk()
root.title("BT1 GUI Encrypt Tool")
root.geometry("560x320")
notebook = ttk.Notebook(root)
frame_pack = tk.Frame(notebook, padx=10, pady=10)
frame_unpack = tk.Frame(notebook, padx=10, pady=10)
frame_setting = tk.Frame(notebook, padx=10, pady=10)
notebook.add(frame_pack, text="📦 Pack Files")
notebook.add(frame_unpack, text="🧹 Unpack")
notebook.add(frame_setting, text="⚙️ Settings")
notebook.pack(fill="both", expand=True)

# === Pack Tab ===
tk.Label(frame_pack, text="Input File:").grid(row=0, column=0, sticky="w")
entry_pack_input = tk.Entry(frame_pack, width=50)
entry_pack_input.grid(row=1, column=0)
tk.Button(frame_pack, text="Choose", command=lambda: pick_file(entry_pack_input)).grid(row=1, column=1)

tk.Label(frame_pack, text="Save As:").grid(row=2, column=0, sticky="w")
entry_pack_output = tk.Entry(frame_pack, width=50)
entry_pack_output.grid(row=3, column=0)
tk.Button(frame_pack, text="Choose", command=lambda: pick_output_file(entry_pack_output)).grid(row=3, column=1)

tk.Button(frame_pack, text="🚀 Pack File", command=pack_file).grid(row=4, column=0, pady=10)

# === Unpack Tab ===
tk.Label(frame_unpack, text="Input .bt1 File:").grid(row=0, column=0, sticky="w")
entry_unpack_input = tk.Entry(frame_unpack, width=50)
entry_unpack_input.grid(row=1, column=0)
tk.Button(frame_unpack, text="Choose", command=lambda: pick_file(entry_unpack_input)).grid(row=1, column=1)

tk.Label(frame_unpack, text="Output Directory:").grid(row=2, column=0, sticky="w")
entry_unpack_output = tk.Entry(frame_unpack, width=50)
entry_unpack_output.grid(row=3, column=0)
tk.Button(frame_unpack, text="Choose", command=lambda: pick_folder(entry_unpack_output)).grid(row=3, column=1)

tk.Button(frame_unpack, text="🔓 Unpack", command=unpack_file).grid(row=4, column=0, pady=10)

# === Settings Tab ===
tk.Label(frame_setting, text="🔐 Password:").grid(row=0, column=0, sticky="w")
entry_pass = tk.Entry(frame_setting, width=30)
entry_pass.insert(0, global_config.get("password", ""))
entry_pass.grid(row=0, column=1)

tk.Label(frame_setting, text="🧂 Salt (hex):").grid(row=1, column=0, sticky="w")
entry_salt = tk.Entry(frame_setting, width=30)
entry_salt.insert(0, global_config.get("salt", ""))
entry_salt.grid(row=1, column=1)

def toggle_dark():
    global_config['dark_mode'] = not global_config['dark_mode']
    save_config()
    apply_theme()

chk_dark = tk.Checkbutton(frame_setting, text="🌙 Enable Dark Mode", command=toggle_dark)
chk_dark.grid(row=2, column=0, columnspan=2, sticky="w")
chk_dark.select() if global_config['dark_mode'] else chk_dark.deselect()

def save_settings():
    global_config['password'] = entry_pass.get()
    global_config['salt'] = entry_salt.get()
    save_config()
    messagebox.showinfo("OK", "Settings saved")

def reset_settings():
    global_config['password'] = "test1"
    global_config['salt'] = ""
    entry_pass.delete(0, tk.END)
    entry_pass.insert(0, "test1")
    entry_salt.delete(0, tk.END)
    save_config()
    apply_theme()
    messagebox.showinfo("Reset", "Settings reset to default")

tk.Button(frame_setting, text="📀 Save", command=save_settings).grid(row=3, column=0)
tk.Button(frame_setting, text="🔄 Reset to Default", command=reset_settings).grid(row=3, column=1)

# === Initialize Theme ===
apply_theme()
root.mainloop()

