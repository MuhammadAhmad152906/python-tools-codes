import tkinter as tk
from tkinter import messagebox

def text_to_binary():
    """Convert entered text to binary representation."""
    text = text_entry.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Input Error", "Please enter some text.")
        return
    
    try:
        binary_str = ' '.join(format(ord(char), '08b') for char in text)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, binary_str)
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed: {e}")

def binary_to_text():
    """Convert entered binary string to text."""
    binary_str = text_entry.get("1.0", tk.END).strip()
    if not binary_str:
        messagebox.showwarning("Input Error", "Please enter binary data.")
        return
    
    try:
        # Validate binary input
        bits = binary_str.split()
        if not all(len(b) == 8 and set(b) <= {"0", "1"} for b in bits):
            raise ValueError("Invalid binary format. Use 8-bit binary values separated by spaces.")
        
        text = ''.join(chr(int(b, 2)) for b in bits)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, text)
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed: {e}")

def save_binary_file():
    """Save the binary output to a file."""
    binary_data = output_text.get("1.0", tk.END).strip()
    if not binary_data:
        messagebox.showwarning("Save Error", "No binary data to save.")
        return
    
    try:
        bits = binary_data.split()
        if not all(len(b) == 8 and set(b) <= {"0", "1"} for b in bits):
            raise ValueError("Output is not valid binary data.")
        
        with open("binary_output.bin", "wb") as f:
            f.write(bytes(int(b, 2) for b in bits))
        messagebox.showinfo("Success", "Binary file saved as binary_output.bin")
    except Exception as e:
        messagebox.showerror("Error", f"File save failed: {e}")

# Create main window
root = tk.Tk()
root.title("Text ↔ Binary Converter")
root.geometry("650x450")
root.resizable(False, False)

# Input label & text box
tk.Label(root, text="Enter Text or Binary:", font=("Arial", 12)).pack(pady=5)
text_entry = tk.Text(root, height=5, width=75)
text_entry.pack()

# Buttons frame
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Text → Binary", command=text_to_binary, bg="#4CAF50", fg="white", width=15).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Binary → Text", command=binary_to_text, bg="#FF9800", fg="white", width=15).grid(row=0, column=1, padx=5)

# Output label & text box
tk.Label(root, text="Output:", font=("Arial", 12)).pack(pady=5)
output_text = tk.Text(root, height=5, width=75)
output_text.pack()

# Save button
tk.Button(root, text="Save Output as Binary File", command=save_binary_file, bg="#2196F3", fg="white").pack(pady=10)

# Run the GUI loop
root.mainloop()
