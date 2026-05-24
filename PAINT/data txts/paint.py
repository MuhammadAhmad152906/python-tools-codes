import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import ImageGrab
import math

class UltimatePaint:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Paint App")

        # Canvas
        self.canvas = tk.Canvas(root, bg="white", width=1000, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variables
        self.old_x = None
        self.old_y = None
        self.pen_color = "black"
        self.fill_color = ""
        self.pen_size = 3
        self.current_tool = "freehand"
        self.shape_id = None
        self.styles = self.generate_styles()
        self.current_style = "solid_round_round_0"

        # Bind events
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
        for tool in ["Freehand","Line","Rectangle","Oval","Text","Eraser"]:
            tk.Button(tool_frame, text=tool, command=lambda t=tool.lower(): self.set_tool(t)).pack(side=tk.LEFT, padx=5)

        # Style selector + preview
        style_frame = tk.Frame(root)
        style_frame.pack(fill=tk.X)
        self.style_var = tk.StringVar(value=self.current_style)
        style_menu = tk.OptionMenu(style_frame, self.style_var, *self.styles.keys(), command=lambda _: self.update_preview())
        style_menu.pack(side=tk.LEFT, padx=5)
        self.preview_canvas = tk.Canvas(style_frame, bg="white", width=200, height=60)
        self.preview_canvas.pack(side=tk.LEFT, padx=5)
        self.update_preview()

        # Template buttons
        template_frame = tk.Frame(root)
        template_frame.pack(fill=tk.X)
        tk.Button(template_frame, text="Circle Grid", command=self.draw_circle_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(template_frame, text="Hexagon Grid", command=self.draw_hexagon_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(template_frame, text="Spiral", command=self.draw_spiral).pack(side=tk.LEFT, padx=5)

    def generate_styles(self):
        styles = {}
        base_caps = ["round","butt","projecting"]
        base_joins = ["round","bevel","miter"]
        patterns = ["solid","dashed","dotted","airbrush","marker","calligraphy","spray","pencil"]
        count=0
        for cap in base_caps:
            for join in base_joins:
                for pat in patterns:
                    styles[f"{pat}_{cap}_{join}_{count}"]={"capstyle":cap,"joinstyle":join,"pattern":pat}
                    count+=1
                    if count>=100: return styles
        return styles

    def set_tool(self, tool): self.current_tool=tool

    def start_draw(self, event):
        self.old_x,self.old_y=event.x,event.y
        if self.current_tool=="text":
            text=simpledialog.askstring("Text Tool","Enter text:")
            if text:
                self.canvas.create_text(event.x,event.y,text=text,
                                        fill=self.pen_color,font=("Arial",self.size_slider.get()*2))
        elif self.current_tool!="freehand": self.shape_id=None

    def draw(self,event):
        self.pen_size=self.size_slider.get()
        style=self.styles[self.style_var.get()]
        if self.current_tool=="freehand":
            if self.old_x and self.old_y:
                self.apply_style(self.old_x,self.old_y,event.x,event.y,style)
            self.old_x,self.old_y=event.x,event.y
        elif self.current_tool=="eraser":
            self.canvas.create_line(self.old_x,self.old_y,event.x,event.y,
                                    width=self.pen_size,fill="white",capstyle="round")
            self.old_x,self.old_y=event.x,event.y
        else:
            if self.shape_id: self.canvas.delete(self.shape_id)
            if self.current_tool=="line":
                self.shape_id=self.canvas.create_line(self.old_x,self.old_y,event.x,event.y,
                                                      width=self.pen_size,fill=self.pen_color)
            elif self.current_tool=="rectangle":
                self.shape_id=self.canvas.create_rectangle(self.old_x,self.old_y,event.x,event.y,
                                                           outline=self.pen_color,width=self.pen_size,
                                                           fill=self.fill_color)
            elif self.current_tool=="oval":
                self.shape_id=self.canvas.create_oval(self.old_x,self.old_y,event.x,event.y,
                                                      outline=self.pen_color,width=self.pen_size,
                                                      fill=self.fill_color)

    def apply_style(self,x1,y1,x2,y2,style):
        if style["pattern"]=="dashed":
            self.canvas.create_line(x1,y1,x2,y2,width=self.pen_size,fill=self.pen_color,
                                    dash=(4,2),capstyle=style["capstyle"])
        elif style["pattern"]=="dotted":
            self.canvas.create_line(x1,y1,x2,y2,width=self.pen_size,fill=self.pen_color,
                                    dash=(1,3),capstyle=style["capstyle"])
        elif style["pattern"]=="airbrush":
            for i in range(5):
                self.canvas.create_oval(x2+i,y2+i,x2+i+2,y2+i+2,fill=self.pen_color,outline="")
        elif style["pattern"]=="spray":
            for i in range(10):
                self.canvas.create_oval(x2+i,y2-i,x2+i+1,y2-i+1,fill=self.pen_color,outline="")
        else:
            self.canvas.create_line(x1,y1,x2,y2,width=self.pen_size,fill=self.pen_color,
                                    capstyle=style["capstyle"],joinstyle=style["joinstyle"])

    def reset(self,event): self.old_x,self.old_y=None,None; self.shape_id=None
    def choose_stroke(self): c=colorchooser.askcolor()[1]; 
        self.pen_color=c if c else self.pen_color
    def choose_fill(self): c=colorchooser.askcolor()[1]; 
        self.fill_color=c if c else self.fill_color
    def clear_canvas(self): self.canvas.delete("all")
    def save_canvas(self):
        x=self.root.winfo_rootx()+self.canvas.winfo_x()
        y=self.root.winfo_rooty()+self.canvas.winfo_y()
        x1=x+self.canvas.winfo_width(); y1=y+self.canvas.winfo_height()
        filepath=filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG files","*.png")])
        if filepath: ImageGrab.grab().crop((x,y,x1,y1)).save(filepath)

    def update_preview(self):
        self.preview_canvas.delete("all")
        style=self.styles[self.style_var.get()]
        self.preview_canvas.create_line(10,30,180,30,width=self.pen_size,fill=self.pen_color,
                                        dash=(4,2) if style["pattern"]=="dashed" else None,
                                        capstyle=style["capstyle"])

    # Templates
    def draw_circle_grid(self):
        for i in range(50,500,50):
            self.canvas.create_oval(100-i,100-i,100+i,100+i,outline="gray")

    def draw_hexagon_grid(self):
        size=50
        for row in range(5):
            for col in range(5):
                x=col*size*1.5+100; y=row*size*math.sqrt(3)+100
                points=[x,y,x+size,y,x+size*1.5,y+size*math.sqrt(3)/2,
                        x+size,y+size*math.sqrt(3),x,y+size*math.sqrt(3),
                        x-size/2,y+size*math.sqrt(3)/2]
                self.canvas.create_polygon(points,outline="gray",fill="")

def draw_spiral(self):
        old_sx, old_sy = None, None
        center_x, center_y = 500, 350  # Center of your 1000x700 canvas
        
        for t in range(0, 360 * 5, 5):
            radians = math.radians(t)
            r = 0.1 * t  # Controls how fast the spiral expands
            
            # Complete the math here
            x = center_x + r * math.cos(radians)
            y = center_y + r * math.sin(radians)
            
            if old_sx is not None and old_sy is not None:
                self.canvas.create_line(old_sx, old_sy, x, y, fill=self.pen_color, width=self.pen_size)
            
            old_sx, old_sy = x, y