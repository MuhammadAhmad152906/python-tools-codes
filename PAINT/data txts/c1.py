import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import ImageGrab

class MultiToolPaint:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Tool Paint")

        # Canvas setup
        self.canvas = tk.Canvas(root, bg="white", width=900, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variables
        self.old_x = None
        self.old_y = None
        self.pen_color = "black"
        self.fill_color = ""
        self.pen_size = 3
        self.current_tool = "freehand"
        self.shape_id = None

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        # Control panel
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X)

        tk.Button(control_frame, text="Stroke Color", command=self.choose_stroke).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Fill Color", command=self.choose_fill).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save", command=self.save_canvas).pack(side=tk.LEFT, padx=5)

        # Brush size slider
        self.size_slider = tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, label="Brush Size")
        self.size_slider.set(self.pen_size)
        self.size_slider.pack(side=tk.LEFT, padx=5)

        # Tool selection
        tool_frame = tk.Frame(root)
        tool_frame.pack(fill=tk.X)

        tk.Button(tool_frame, text="Freehand", command=lambda: self.set_tool("freehand")).pack(side=tk.LEFT, padx=5)
        tk.Button(tool_frame, text="Line", command=lambda: self.set_tool("line")).pack(side=tk.LEFT, padx=5)
        tk.Button(tool_frame, text="Rectangle", command=lambda: self.set_tool("rectangle")).pack(side=tk.LEFT, padx=5)
        tk.Button(tool_frame, text="Oval", command=lambda: self.set_tool("oval")).pack(side=tk.LEFT, padx=5)
        tk.Button(tool_frame, text="Text", command=lambda: self.set_tool("text")).pack(side=tk.LEFT, padx=5)

    def set_tool(self, tool):
        self.current_tool = tool

    def start_draw(self, event):
        self.old_x, self.old_y = event.x, event.y
        if self.current_tool == "text":
            text = simpledialog.askstring("Text Tool", "Enter text:")
            if text:
                self.canvas.create_text(event.x, event.y, text=text,
                                        fill=self.pen_color, font=("Arial", self.size_slider.get()*2))
        elif self.current_tool != "freehand":
            self.shape_id = None

    def draw(self, event):
        self.pen_size = self.size_slider.get()
        if self.current_tool == "freehand":
            if self.old_x and self.old_y:
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                        width=self.pen_size, fill=self.pen_color,
                                        capstyle=tk.ROUND, smooth=True)
            self.old_x, self.old_y = event.x, event.y
        else:
            if self.shape_id:
                self.canvas.delete(self.shape_id)
            if self.current_tool == "line":
                self.shape_id = self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                                        width=self.pen_size, fill=self.pen_color)
            elif self.current_tool == "rectangle":
                self.shape_id = self.canvas.create_rectangle(self.old_x, self.old_y, event.x, event.y,
                                                             outline=self.pen_color, width=self.pen_size,
                                                             fill=self.fill_color)
            elif self.current_tool == "oval":
                self.shape_id = self.canvas.create_oval(self.old_x, self.old_y, event.x, event.y,
                                                        outline=self.pen_color, width=self.pen_size,
                                                        fill=self.fill_color)

    def reset(self, event):
        self.old_x, self.old_y = None, None
        self.shape_id = None

    def choose_stroke(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.pen_color = color

    def choose_fill(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.fill_color = color

    def clear_canvas(self):
        self.canvas.delete("all")

    def save_canvas(self):
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png")])
        if filepath:
            ImageGrab.grab().crop((x, y, x1, y1)).save(filepath)

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiToolPaint(root)
    root.mainloop()
