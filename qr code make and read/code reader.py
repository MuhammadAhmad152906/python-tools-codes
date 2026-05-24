import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import os

def read_qr_from_image():
    """Open file dialog and read QR code from selected image."""
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if not file_path:
        return

    if not os.path.exists(file_path):
        messagebox.showerror("Error", "File not found.")
        return

    try:
        img = Image.open(file_path)
        decoded_objects = decode(img)
        output_box.delete("1.0", tk.END)
        if not decoded_objects:
            output_box.insert(tk.END, "No QR code found in image.")
        else:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                qr_type = obj.type
                output_box.insert(tk.END, f"Type: {qr_type}\nData: {qr_data}\n\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read image: {e}")

def read_qr_from_webcam():
    """Read QR code from live webcam feed."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Webcam not found.")
        return

    messagebox.showinfo("Webcam", "Press 'q' in the webcam window to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            qr_type = obj.type
            output_box.delete("1.0", tk.END)
            output_box.insert(tk.END, f"Type: {qr_type}\nData: {qr_data}\n\n")

            # Draw rectangle around QR code
            pts = obj.polygon
            pts = [(p.x, p.y) for p in pts]
            for i in range(len(pts)):
                cv2.line(frame, pts[i], pts[(i+1) % len(pts)], (0, 255, 0), 2)

        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Create main window
root = tk.Tk()
root.title("QR Code Reader")
root.geometry("500x400")
root.resizable(False, False)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Scan from Image", command=read_qr_from_image, bg="#4CAF50", fg="white", width=20).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Scan from Webcam", command=read_qr_from_webcam, bg="#2196F3", fg="white", width=20).grid(row=0, column=1, padx=5)

# Output box
tk.Label(root, text="Decoded QR Code Data:", font=("Arial", 12)).pack(pady=5)
output_box = scrolledtext.ScrolledText(root, height=15, width=60, wrap=tk.WORD)
output_box.pack(pady=5)

# Run GUI
root.mainloop()
