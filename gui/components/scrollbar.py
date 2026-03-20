import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from gui.components.animated_image import AnimatedImage


class MyScrollbar(tk.Canvas):
    def __init__(
        self,
        parent,
        target,
        command,
        orient="vertical",
        thickness=14,
        thumb_thickness=10,
        background_color="black",
        thumb_color="white",
        line_color="gray",
        **kwargs
    ):
        super().__init__(
            parent,
            background=background_color,
            border=0,
            highlightthickness=0,
            **kwargs
        )
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.tin = 1.4
        self.thickness = thickness
        self.thumb_thickness = thumb_thickness
        self.thumb_color = thumb_color
        self.target = target
        self.image_dictionary = {}
        self.image_count = 0
        self.thumb_thickness = thumb_thickness
        self.command = command
        self.gap = (thickness - thumb_thickness) / 2
        self.pad = 16
        self.line_color = line_color

        bbox = self.bbox_calculate()
        self.thumb = self.create_rectangle(bbox, fill=line_color, outline="")
        self.config(width=thickness)
        self.addtag_withtag("thumb", self.thumb)
        self.tag_bind("thumb", "<B1-Motion>", self.button_motion)
        self.tag_bind("thumb", "<Button-1>", self.button_click)
        self.tag_bind("thumb", "<ButtonRelease-1>", self.rebind)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.tag_bind("thumb", "<Enter>", self.thumb_enter)
        self.tag_bind("thumb", "<Leave>", self.thumb_leave)
        parent.bind("<Configure>", self.resize)
        self.up_arrow_image = self.draw_triangle(10, 10, thumb_color)
        self.down_arrow_image = self.draw_triangle(10, 10, thumb_color, side="bottom")
        self.up_arrow = AnimatedImage(
            self, bg=background_color, image_path=self.up_arrow_image, cursor="hand2"
        )
        self.down_arrow = AnimatedImage(
            self, bg=background_color, image_path=self.down_arrow_image, cursor="hand2"
        )
        self.up_arrow.image = self.up_arrow_image
        self.down_arrow.image = self.down_arrow_image
        self.up_arrow.pack(side=tk.TOP, fill="x")
        self.down_arrow.pack(side=tk.BOTTOM, fill="x")
        self.up_arrow.bind("<Button-1>", self.up_arrow_click)
        self.down_arrow.bind("<Button-1>", self.down_arrow_click)

    def resize(self, e):
        bbox = self.bbox_calculate()
        self.coords(self.thumb, bbox)

    def draw_triangle(self, height, taban, color="black", side="top"):
        temp_height = height * 4
        temp_taban = taban * 4
        image = Image.new("RGBA", (temp_taban, temp_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        if side == "top":
            tepe = temp_taban / 2
            bbox = ((tepe, 0), (0, temp_height), (temp_taban, temp_height))
        elif side == "bottom":
            tepe = temp_taban / 2
            bbox = ((tepe, temp_height), (0, 0), (temp_taban, 0))
        draw.polygon(bbox, fill=color, outline=None)
        image = image.resize((taban, height), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(image)
        return image

    def draw_rectangle(self, x, y, width, height, fill="white"):
        item = self.create_rectangle(
            x,
            y,
            float(x) + float(width),
            float(y) + float(height),
            fill=fill,
            outline="",
        )
        return item

    def button_click(self, event):
        coords = self.coords(self.thumb)
        self.starty = event.y - coords[1]

    def rebind(self, e):
        self.bind("<Leave>", self.on_leave)
        self.bind("<Enter>", self.on_enter)

    def bbox_calculate(self):
        bbox = [
            self.gap,
            self.command()[0] * (self.winfo_height() - 2 * self.pad) + self.pad,
            self.gap + self.thumb_thickness,
            self.command()[1] * (self.winfo_height() - 2 * self.pad) + self.pad,
        ]
        return bbox

    def button_motion(self, event):
        self.unbind("<Leave>")
        self.unbind("<Enter>")
        if event.y - self.starty > self.pad:
            if event.y - self.starty + self.pad < self.winfo_height():
                a = float(
                    (event.y - self.starty - self.pad)
                    / (self.winfo_height() - 2 * self.pad)
                )
                self.target.yview_moveto(a)
                bbox = self.bbox_calculate()
                self.coords(self.thumb, bbox)

            else:
                self.target.yview_moveto(1.0)
                bbox = self.bbox_calculate()
                self.coords(self.thumb, bbox)
        else:
            self.target.yview_moveto(0)
            bbox = self.bbox_calculate()
            self.coords(self.thumb, bbox)

    def set(self, first, last):
        bbox = [
            self.gap,
            float(first) * (self.winfo_height() - 2 * self.pad) + self.pad,
            self.gap + self.thumb_thickness,
            float(last) * (self.winfo_height() - 2 * self.pad) + self.pad,
        ]
        a = self.coords(self.thumb, bbox)

    def thumb_enter(self, e):
        self.config(cursor="hand2")

    def thumb_leave(self, e):
        self.config(cursor="")

    def on_enter(self, e):
        self.thumb_thickness = self.thumb_thickness + 2 * self.tin
        self.gap = self.gap - self.tin
        bbox = self.bbox_calculate()
        self.coords(self.thumb, bbox)
        self.up_arrow.event_arttir(1)
        self.down_arrow.event_arttir(1)
        self.itemconfig(self.thumb, fill=self.thumb_color)

    def on_leave(self, e):
        self.thumb_thickness = self.thumb_thickness - 2 * self.tin
        self.gap = (self.thickness - self.thumb_thickness) / 2
        bbox = self.bbox_calculate()
        self.coords(self.thumb, bbox)
        self.up_arrow.event_azalt(1)
        self.down_arrow.event_azalt(1)
        self.itemconfig(self.thumb, fill=self.line_color)

    def up_arrow_click(self, e):
        self.target.yview_scroll(-1, "units")

    def down_arrow_click(self, e):
        self.target.yview_scroll(1, "units")
