import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import barcode
from barcode.writer import ImageWriter
import segno
import io, os, json, csv

# -------------------------------
# Code Generators
# -------------------------------
def generate_qr(data, fill_color="black", back_color="white", error_level="H", box_size=10):
    qr = qrcode.QRCode(
        version=2,
        error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_level}"),
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color=fill_color, back_color=back_color)

def generate_barcode(data):
    code128 = barcode.get_barcode_class('code128')
    bar = code128(data, writer=ImageWriter())
    buffer = io.BytesIO()
    bar.write(buffer)
    buffer.seek(0)
    return Image.open(buffer)

def generate_data_matrix(data, scale=5):
    dm = segno.make(data, micro=False, error='h')
    buffer = io.BytesIO()
    dm.save(buffer, kind='png', scale=scale)
    buffer.seek(0)
    return Image.open(buffer)

# -------------------------------
# Helper Functions
# -------------------------------
def show_image(img, label):
    img.thumbnail((300, 300))
    tk_img = ImageTk.PhotoImage(img)
    label.config(image=tk_img)
    label.image = tk_img

def save_image(img, default_name):
    filename = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default_name,
                                            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")])
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            img.save(filename, "PDF")
        else:
            img.save(filename)
        messagebox.showinfo("Success", f"Saved as {filename}")

def add_to_history(img, title, default_name):
    img_copy = img.copy()
    history_items.append((title, img_copy, default_name))
    update_history_list()
    save_history_to_disk()

def update_history_list():
    history_list.delete(0, tk.END)
    for i, (title, _, _) in enumerate(history_items):
        history_list.insert(tk.END, f"{i+1}. {title}")

def show_history_preview(event):
    selection = history_list.curselection()
    if selection:
        index = selection[0]
        _, img, _ = history_items[index]
        show_image(img, history_label)

def re_export_selected():
    selection = history_list.curselection()
    if selection:
        index = selection[0]
        _, img, default_name = history_items[index]
        save_image(img, default_name)
    else:
        messagebox.showerror("Error", "Please select an item from history")

def save_history_to_disk():
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump([title for title, _, _ in history_items], f)

def load_history_from_disk():
    if os.path.exists("history.json"):
        with open("history.json", "r", encoding="utf-8") as f:
            titles = json.load(f)
        for title in titles:
            history_items.append((title, Image.new("RGB", (300, 300), "white"), "restored.png"))
        update_history_list()

# -------------------------------
# Batch Generation
# -------------------------------
def batch_generate():
    file_path = filedialog.askopenfilename(filetypes=[("CSV/JSON files", "*.csv *.json")])
    if not file_path:
        return
    if file_path.endswith(".csv"):
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    img = generate_qr(row[0])
                    add_to_history(img, f"Batch QR: {row[0]}", "batch_qr.png")
    elif file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                img = generate_qr(item)
                add_to_history(img, f"Batch QR: {item}", "batch_qr.png")
    messagebox.showinfo("Batch", "Batch generation complete")

# -------------------------------
# NFC / RFID Placeholders
# -------------------------------
def handle_nfc(entry):
    data = entry.get()
    messagebox.showinfo("NFC", f"NFC writing placeholder.\nData: {data}")

def handle_rfid(entry):
    data = entry.get()
    messagebox.showinfo("RFID", f"RFID writing placeholder.\nData: {data}")

# -------------------------------
# GUI Setup
# -------------------------------
root = tk.Tk()
root.title("Advanced Code Generator - Full Suite")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

history_items = []
load_history_from_disk()

# --- QR Tab ---
qr_tab = ttk.Frame(notebook)
notebook.add(qr_tab, text="QR Code")
qr_entry = tk.Entry(qr_tab, width=50)
qr_entry.pack(pady=5)
qr_label = tk.Label(qr_tab)
qr_label.pack(pady=10)

def handle_qr():
    data = qr_entry.get()
    if not data:
        messagebox.showerror("Error", "Please enter data")
        return
    img = generate_qr(data)
    show_image(img, qr_label)
    save_image(img, "qr_code.png")
    add_to_history(img, f"QR: {data}", "qr_code.png")

tk.Button(qr_tab, text="Generate QR", command=handle_qr).pack(pady=5)
tk.Button(qr_tab, text="Batch Generate", command=batch_generate).pack(pady=5)

# --- Barcode Tab ---
bar_tab = ttk.Frame(notebook)
notebook.add(bar_tab, text="Barcode")
bar_entry = tk.Entry(bar_tab, width=50)
bar_entry.pack(pady=5)
bar_label = tk.Label(bar_tab)
bar_label.pack(pady=10)
tk.Button(bar_tab, text="Generate Barcode", command=lambda: handle_barcode(bar_entry, bar_label)).pack(pady=5)

def handle_barcode(entry, label):
    data = entry.get()
    if not data:
        messagebox.showerror("Error", "Please enter data")
        return
    img = generate_barcode(data)
    show_image(img, label)
    save_image(img, "barcode.png")
    add_to_history(img, f"Barcode: {data}", "barcode.png")

# --- Data Matrix Tab ---
dm_tab = ttk.Frame(notebook)
notebook.add(dm_tab, text="Data Matrix")
dm_entry = tk.Entry(dm_tab, width=50)
dm_entry.pack(pady=5)
dm_label = tk.Label(dm_tab)
dm_label.pack(pady=10)
tk.Button(dm_tab, text="Generate Data Matrix", command=lambda: handle_datamatrix(dm_entry, dm_label)).pack(pady=5)

def handle_datamatrix(entry, label):
    data = entry.get()
    if not data:
        messagebox.showerror("Error", "Please enter data")
        return
    img = generate_data_matrix(data)
    show_image(img, label)
    save_image(img, "datamatrix.png")
    add_to_history(img, f"DataMatrix: {data}", "datamatrix.png")

# --- NFC Tab ---
nfc_tab = ttk.Frame(notebook)
notebook.add(nfc_tab, text="NFC")
nfc_entry = tk.Entry(nfc_tab, width=50)
nfc_entry.pack(pady=5)
tk.Button(nfc_tab, text="Write NFC Tag", command=lambda: handle_nfc(nfc_entry)).pack(pady=5)

# --- RFID Tab ---
rfid_tab = ttk.Frame(notebook)
notebook.add(rfid_tab, text="RFID")
rfid_entry = tk.Entry(rfid_tab, width=50)
rfid_entry.pack(pady=5)
tk.Button(rfid_tab, text="Write RFID Tag", command=lambda: handle_rfid(rfid_entry)).pack(pady=5)

# --- History Tab ---
history_tab = ttk.Frame(notebook)
notebook.add(history_tab, text="History")
history_list = tk.Listbox(history_tab, width=50, height=10)
history_list.pack(side="left", fill="y", padx=5, pady=5)
history_list.bind("<<ListboxSelect>>", show_history_preview)
history_label = tk.Label(history_tab)
history_label.pack(side="top", padx=10, pady=10)
tk.Button(history_tab, text="Re-Export Selected", command=re_export_selected).pack(side="bottom", pady=10)

root.mainloop()
