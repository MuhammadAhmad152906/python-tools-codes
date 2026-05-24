import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import ImageGrab

class MultiBrushPaint:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Brush Paint")

        # Canvas
        self.canvas = tk.Canvas(root, bg="white", width=900, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variables
        self.old_x = None
        self.old_y = None
        self.pen_color = "black"
        self.pen_size = 3
        self.current_style = "solid"
        self.styles = self.generate_styles()  # 80–100 styles

        # Bind events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        # Control panel
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X)

        tk.Button(control_frame, text="Stroke Color", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save", command=self.save_canvas).pack(side=tk.LEFT, padx=5)

        # Brush size slider
        self.size_slider = tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, label="Brush Size")
        self.size_slider.set(self.pen_size)
        self.size_slider.pack(side=tk.LEFT, padx=5)

        # Style selector
        style_frame = tk.Frame(root)
        style_frame.pack(fill=tk.X)
        self.style_var = tk.StringVar(value=self.current_style)
        style_menu = tk.OptionMenu(style_frame, self.style_var, *self.styles.keys())
        style_menu.pack(side=tk.LEFT, padx=5)

    def generate_styles(self):
        # Define 80–100 brush styles
        styles = {}
        base_caps = ["round", "butt", "projecting"]
        base_joins = ["round", "bevel", "miter"]
        patterns = ["solid", "dashed", "dotted", "airbrush", "marker", "calligraphy", "spray", "pencil"]

        count = 0
        for cap in base_caps:
            for join in base_joins:
                for pat in patterns:
                    styles[f"{pat}_{cap}_{join}_{count}"] = {
                        "capstyle": cap,
                        "joinstyle": join,
                        "pattern": pat
                    }
                    count += 1
                    if count >= 100:
                        return styles
        return styles

    def set_style(self):
        self.current_style = self.style_var.get()

    def start_draw(self, event):
        self.old_x, self.old_y = event.x, event.y

    def draw(self, event):
        self.pen_size = self.size_slider.get()
        style = self.styles[self.style_var.get()]
        if self.old_x and self.old_y:
            if style["pattern"] == "dashed":
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                        width=self.pen_size, fill=self.pen_color,
                                        dash=(4, 2), capstyle=style["capstyle"])
            elif style["pattern"] == "dotted":
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                        width=self.pen_size, fill=self.pen_color,
                                        dash=(1, 3), capstyle=style["capstyle"])
            elif style["pattern"] == "airbrush":
                for i in range(5):
                    self.canvas.create_oval(event.x, event.y, event.x+2, event.y+2,
                                            fill=self.pen_color, outline="")
            elif style["pattern"] == "spray":
                for i in range(10):
                    self.canvas.create_oval(event.x+i, event.y+i, event.x+i+1, event.y+i+1,
                                            fill=self.pen_color, outline="")
            else:  # solid, marker, calligraphy, pencil
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                        width=self.pen_size, fill=self.pen_color,
                                        capstyle=style["capstyle"], joinstyle=style["joinstyle"])
        self.old_x, self.old_y = event.x, event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.pen_color = color

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
    app = MultiBrushPaint(root)
    root.mainloop()
