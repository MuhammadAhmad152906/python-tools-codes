def update_preview(self):
    self.preview_canvas.delete("all")
    style = self.styles[self.style_var.get()]
    # Draw sample stroke
    self.preview_canvas.create_line(10, 30, 180, 30,
                                    width=self.pen_size,
                                    fill=self.pen_color,
                                    dash=(4, 2) if style["pattern"]=="dashed" else None,
                                    capstyle=style["capstyle"])
