self.canvas.postscript(file="drawing.ps")
from PIL import Image
img = Image.open("drawing.ps")
img.save("drawing.png")
