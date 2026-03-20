import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class SwitchButton(tk.Canvas):
    def __init__(
        self,
        parent,
        active_function,
        pasif_function,
        f="#79918b",
        s="#79918b",
        status=False,
        width=50,
        height=25,
        g=1.4,
        **kwargs,
    ):
        super().__init__(
            parent,
            cursor="hand2",
            background=parent.cget("bg"),
            width=width,
            height=height,
            **kwargs,
        )
        self.parent = parent
        self.status = status
        self.active_function = active_function
        self.pasif_function = pasif_function
        self.f = f
        self.s = s
        self.g = g
        self.i = 0
        self.w = width - 2
        self.h = height - 2
        self.image_dictionary = {}
        self.image_count = 0
        outside_color = "#79918b"
        inside_color = "#394240"
        self.inside_color = inside_color
        self.outside_color = outside_color
        if status == False:
            inner_color = f
        else:
            inner_color = s
        self.draw_backside(inner_color)
        if not status:
            self.circle = self.draw_smooth_circle(
                2 * g, 2 * g, int(self.h - 4 * self.g), fill=inside_color
            )
        else:
            self.circle = self.draw_smooth_circle(
                self.w - 2 * self.g - (self.h - 4 * self.g),
                2 * self.g,
                int(self.h - 4 * self.g),
                fill=inside_color,
            )
        self.addtag_withtag("switch", self.circle)
        self.tag_bind("switch", "<Button-1>", self.animation)

    def draw_backside(self, color):
        self.delete("outer")
        self.image_dictionary = {}
        self.north = self.draw_smooth_arc(
            x=0, y=0, radius=self.h, start=90, end=270, fill=color
        )
        self.south = self.draw_smooth_arc(
            x=self.w - self.h, y=0, radius=self.h, start=270, end=90, fill=color
        )
        self.rect = self.draw_rectangle(
            x=int(self.h / 2),
            y=0,
            width=int(self.w - self.h),
            height=self.h,
            fill=color,
        )
        self.addtag_withtag("switch", self.north)
        self.addtag_withtag("switch", self.south)
        self.addtag_withtag("switch", self.rect)
        self.addtag_withtag("outer", self.north)
        self.addtag_withtag("outer", self.south)
        self.addtag_withtag("outer", self.rect)

    def pasif(self):
        self.coords(self.circle, 2 * self.g + self.i, 2 * self.g)
        if self.h - 2 * self.g + self.i + 4 < self.w - 2 * self.g:
            self.i = self.i + 5
            self.parent.after(5, self.pasif)
        else:
            self.status = True
            self.draw_backside(self.s)
            self.delete(self.circle)
            self.circle = self.draw_smooth_circle(
                self.w - 2 * self.g - (self.h - 4 * self.g),
                2 * self.g,
                int(self.h - 4 * self.g),
                fill=self.inside_color,
            )
            self.addtag_withtag("switch", self.circle)
            self.open()

    def active(self):
        self.coords(
            self.circle,
            self.w - 2 * self.g - (self.h - 4 * self.g) + self.i,
            2 * self.g,
        )
        if self.w - 2 * self.g + self.i - 4 > self.h - 2 * self.g:
            self.i = self.i - 5
            self.parent.after(5, self.active)
        else:
            self.status = False
            self.draw_backside(self.f)
            self.delete(self.circle)
            self.circle = self.draw_smooth_circle(
                2 * self.g, 2 * self.g, int(self.h - 4 * self.g), fill=self.inside_color
            )
            self.addtag_withtag("switch", self.circle)
            self.close()

    def animation(self, e):
        if not self.status:
            self.i = 0
            self.pasif()

        elif self.status:
            self.i = 0
            self.active()

    def open(self):
        self.active_function()

    def close(self):
        self.pasif_function()

    def draw_smooth_circle(self, x, y, radius, fill=(255, 0, 0, 255)):
        # Pillow ile antialiasing uygulamak için image oluşturun
        size = 4 * radius
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Daireyi Pillow ile çiz
        draw.ellipse((0, 0, size - 1, size - 1), fill=fill)

        # Antialiasing için resmi küçültün
        image = image.resize((radius, radius), Image.Resampling.LANCZOS)

        # Tkinter Canvas'a Pillow resmi yerleştir
        tk_image = ImageTk.PhotoImage(image)
        item = self.create_image(x, y, image=tk_image, anchor="nw")

        # Resmin tkinter'da tutulması için referans kaybetmeyin
        self.image_dictionary[f"image_{self.image_count}"] = tk_image
        self.image_count += 1
        return item

    def draw_smooth_arc(self, x, y, radius, start, end, fill=(255, 0, 0, 255)):
        # Pillow ile antialiasing uygulamak için image oluşturun
        size = 4 * radius
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Daireyi Pillow ile çiz
        bbox = (0, 0, size - 1, size - 1)
        draw.pieslice(bbox, start, end, fill=fill)

        # Antialiasing için resmi küçültün
        image = image.resize((radius, radius), Image.Resampling.LANCZOS)

        # Tkinter Canvas'a Pillow resmi yerleştir
        tk_image = ImageTk.PhotoImage(image)
        item = self.create_image(x, y, image=tk_image, anchor="nw")

        # Resmin tkinter'da tutulması için referans kaybetmeyin
        self.image_dictionary[f"image_{self.image_count}"] = tk_image
        self.image_count += 1
        return item

    def draw_rectangle(self, x, y, width, height, fill=(255, 0, 0, 255)):
        size1 = width
        size2 = height
        image = Image.new("RGBA", (size1 + 3, size2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        bbox = (0, 0, size1 + 2, size2)
        draw.rectangle(bbox, fill=fill)
        tk_image = ImageTk.PhotoImage(image)
        item = self.create_image(x - 1, y, image=tk_image, anchor="nw")
        self.image_dictionary[f"image_{self.image_count}"] = tk_image
        self.image_count += 1
        return item


class MyButton:
    def __init__(
        self,
        root,
        image: tk.PhotoImage = None,
        width=0,
        height=0,
        text="",
        align_text="west",
        text_pad=0,
        round=0,
        corners=[1, 1, 1, 1],
        background="white",
        text_color="black",
        font=("Helvetica", 12),
    ):
        self.root = root
        self.width = width
        self.height = height
        self.text = text
        self.align_text = align_text
        self.text_pad = text_pad
        self.round = round
        self.corners = corners
        self.background = background
        self.text_color = text_color
        self.font = font
        self.image = image
        # MAIN CANVAS

        self.canvas = tk.Canvas(
            root,
            width=width + 1,
            height=height + 1,
            bg=root.cget("bg"),
            highlightthickness=0,
            borderwidth=0,
            cursor="hand2",
        )
        # ROUND OVALS AND RECTANGLES
        diameter = round * 2
        if corners[0] == 1:
            self.ovalnw = self.canvas.create_arc(
                0,
                0,
                diameter,
                diameter,
                start=90,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalnw)
        else:
            self.rectanglenw = self.canvas.create_rectangle(
                0, 0, round, round, fill=background, outline=""
            )
            self.canvas.addtag_withtag("button", self.rectanglenw)
        if corners[1] == 1:
            self.ovalne = self.canvas.create_arc(
                width - diameter - 1,
                0,
                width - 1,
                diameter,
                start=360,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalne)
        else:
            self.rectanglene = self.canvas.create_rectangle(
                width - round - 1, 0, width - 1, round, fill=background, outline=""
            )
            self.canvas.addtag_withtag("button", self.rectanglene)
        if corners[2] == 1:
            self.ovalsw = self.canvas.create_arc(
                0,
                height - diameter,
                diameter,
                height,
                start=180,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalsw)
        else:
            self.rectanglesw = self.canvas.create_rectangle(
                0, height - round, round, height + 1, fill=background, outline=""
            )
            self.canvas.addtag_withtag("button", self.rectanglesw)
        if corners[3] == 1:
            self.ovalse = self.canvas.create_arc(
                width - diameter - 1,
                height - diameter,
                width - 1,
                height,
                start=270,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalse)
        else:
            self.rectanglese = self.canvas.create_rectangle(
                width - round - 1,
                height - round,
                width - 1,
                height + 1,
                fill=background,
                outline="",
            )
            self.canvas.addtag_withtag("button", self.rectanglese)
        self.rectangle_horizontal = self.canvas.create_rectangle(
            0, round, width, height - round, fill=background, outline=""
        )
        self.rectangle_vertical = self.canvas.create_rectangle(
            round, 0, width - round - 1, height + 1, fill=background, outline=""
        )
        # TEXT
        align_dict = {
            "west": [0, "w"],
            "east": [width - round, "e"],
            "center": [width / 2, "center"],
        }
        if image == None:
            self.widget_text = self.canvas.create_text(
                align_dict[align_text][0] + text_pad,
                height / 2,
                text=text,
                font=font,
                fill=text_color,
                anchor=align_dict[align_text][1],
            )
        else:
            img = self.canvas.create_image(
                align_dict[align_text][0] + text_pad,
                height / 2,
                image=self.image,
                anchor=align_dict[align_text][1],
            )
            self.widget_text = self.canvas.create_text(
                align_dict[align_text][0] + text_pad + self.image.width() + 5,
                height / 2,
                text=text,
                font=font,
                fill=text_color,
                anchor=align_dict[align_text][1],
            )

        # TAG
        self.canvas.addtag_withtag("button", self.rectangle_horizontal)
        self.canvas.addtag_withtag("button", self.rectangle_vertical)

    def update(
        self,
        root,
        image: tk.PhotoImage = None,
        width=0,
        height=0,
        text="",
        align_text="west",
        text_pad=0,
        round=0,
        corners=[1, 1, 1, 1],
        background="white",
        text_color="black",
        font=("Helvetica", 12),
    ):
        # MAIN CANVAS
        self.canvas.config(width=width + 1, height=height + 1)
        for item in self.canvas.find_all():
            self.canvas.delete(item)
        # ROUND OVALS AND RECTANGLES
        diameter = round * 2
        if corners[0] == 1:
            self.ovalnw = self.canvas.create_arc(
                0,
                0,
                diameter,
                diameter,
                start=90,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalnw)
        else:
            self.rectanglenw = self.canvas.create_rectangle(
                0, 0, round, round, fill=background, outline=""
            )
            self.canvas.addtag_withtag("button", self.rectanglenw)
        if corners[1] == 1:
            self.ovalne = self.canvas.create_arc(
                width - diameter - 1,
                0,
                width - 1,
                diameter,
                start=360,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalne)
        else:
            self.rectanglene = self.canvas.create_rectangle(
                width - round - 1, 0, width - 1, round, fill=background, outline=""
            )
            self.canvas.addtag_withtag("button", self.rectanglene)
        if corners[2] == 1:
            self.ovalsw = self.canvas.create_arc(
                0,
                height - diameter,
                diameter,
                height,
                start=180,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalsw)
        else:
            self.rectanglesw = self.canvas.create_rectangle(
                0, height - round, round, height + 1, fill=background, outline=""
            )
            self.canvas.addtag_withtag("button", self.rectanglesw)
        if corners[3] == 1:
            self.ovalse = self.canvas.create_arc(
                width - diameter - 1,
                height - diameter,
                width - 1,
                height,
                start=270,
                extent=90,
                fill=background,
                outline="",
                style=tk.PIESLICE,
            )
            self.canvas.addtag_withtag("button", self.ovalse)
        else:
            self.rectanglese = self.canvas.create_rectangle(
                width - round - 1,
                height - round,
                width - 1,
                height + 1,
                fill=background,
                outline="",
            )
            self.canvas.addtag_withtag("button", self.rectanglese)
        self.rectangle_horizontal = self.canvas.create_rectangle(
            0, round, width, height - round, fill=background, outline=""
        )
        self.rectangle_vertical = self.canvas.create_rectangle(
            round, 0, width - round - 1, height + 1, fill=background, outline=""
        )
        # TEXT
        align_dict = {
            "west": [0, "w"],
            "east": [width - round, "e"],
            "center": [width / 2, "center"],
        }
        if image == None:
            self.widget_text = self.canvas.create_text(
                align_dict[align_text][0] + text_pad,
                height / 2,
                text=text,
                font=font,
                fill=text_color,
                anchor=align_dict[align_text][1],
            )
        else:
            img = self.canvas.create_image(
                align_dict[align_text][0] + text_pad,
                height / 2,
                image=self.image,
                anchor=align_dict[align_text][1],
            )
            self.widget_text = self.canvas.create_text(
                align_dict[align_text][0] + text_pad + self.image.width() + 5,
                height / 2,
                text=text,
                font=font,
                fill=text_color,
                anchor=align_dict[align_text][1],
            )
        # TAG
        self.canvas.addtag_withtag("button", self.rectangle_horizontal)
        self.canvas.addtag_withtag("button", self.rectangle_vertical)

    def config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.update(
            root=self.root,
            image=self.image,
            width=self.width,
            height=self.height,
            text=self.text,
            align_text=self.align_text,
            text_pad=self.text_pad,
            round=self.round,
            corners=self.corners,
            background=self.background,
            text_color=self.text_color,
            font=self.font,
        )

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def grid(self, **kwargs):
        self.canvas.grid(**kwargs)

    def place(self, **kwargs):
        self.canvas.place(**kwargs)

    def tag(self, tag, list):
        for i in list:
            self.canvas.addtag_withtag(tag, i)

    def destroy(self):
        self.canvas.destroy()

    def place_forget(self):
        self.canvas.place_forget()

    def pack_forget(self):
        self.canvas.pack_forget()

    def grid_forget(self):
        self.canvas.grid_forget()

    def bind(self, *args, **kwargs):
        self.canvas.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        self.canvas.unbind(*args, **kwargs)

    def winfo_x(self):
        return self.canvas.winfo_x()

    def winfo_y(self):
        return self.canvas.winfo_y()

    def winfo_width(self):
        return self.canvas.winfo_width()

    def winfo_height(self):
        return self.canvas.winfo_height()

    def place_configure(self, **kwargs):
        self.canvas.place_configure(**kwargs)

    def grid_configure(self, **kwargs):
        self.canvas.grid_configure(**kwargs)

    def pack_configure(self, **kwargs):
        self.canvas.pack_configure(**kwargs)
