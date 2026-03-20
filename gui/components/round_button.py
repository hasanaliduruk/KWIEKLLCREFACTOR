import tkinter as tk


def create_round_button(
    canvas,
    lenght,
    height,
    radius,
    text,
    fill_color,
    text_color,
    corners=[1, 1, 1, 1],
    fonksiyon=None,
    onenter_color="",
    args=(),
    outline_widht=1,
    outline_color="black",
    active_color="white",
    canvas_bg="white",
    active_text_color="black",
    font=("Helvetica", 12),
):
    button_canvas = tk.Canvas(
        canvas,
        height=height + (outline_widht * 2) + 2,
        width=lenght + (outline_widht * 2) + 2,
        border=0,
        bg=canvas_bg,
        highlightthickness=0,
    )
    if outline_widht == 0:
        outline_color = ""
    if onenter_color == "":
        onenter_color = fill_color
    if fonksiyon == None:

        def donothing():
            pass

        fonksiyon = donothing
    button_canvas.pack_propagate(False)
    x = ((outline_widht * 2) + 2) / 2
    y = ((outline_widht * 2) + 2) / 2
    horizontal_rectangle_lenght = lenght - (2 * radius)
    vertical_rectangle_lenght = height - (2 * radius)
    a = horizontal_rectangle_lenght / 2
    # Buton arka planını çiz
    items = []
    if corners[0] == 1:
        oval1 = button_canvas.create_arc(
            x,
            y,
            x + (radius * 2),
            y + (radius * 2),
            start=90,
            extent=90,
            style=tk.PIESLICE,
            fill=fill_color,
            outline="",
        )
        oval1_out = button_canvas.create_arc(
            x,
            y,
            x + (radius * 2),
            y + (radius * 2),
            start=90,
            extent=90,
            style=tk.ARC,
            fill=fill_color,
            outline=outline_color,
            width=outline_widht,
        )  # sol ust oval
        button_canvas.addtag_withtag("button", oval1_out)
        button_canvas.addtag_withtag("button", oval1)
        items.append(oval1)
    else:
        rectnw = button_canvas.create_rectangle(
            x, y, x + (radius * 2), y + (radius * 2), fill=fill_color, outline=""
        )
        items.append(rectnw)
    if corners[1] == 1:
        oval2 = button_canvas.create_arc(
            x + lenght - (2 * radius) - 1,
            y,
            x + lenght - 1,
            y + (radius * 2),
            start=360,
            extent=90,
            style=tk.PIESLICE,
            fill=fill_color,
            outline="",
        )  # sag ust oval
        oval2_out = button_canvas.create_arc(
            x + lenght - (2 * radius),
            y,
            x + lenght,
            y + (radius * 2),
            start=360,
            extent=90,
            style=tk.ARC,
            fill=fill_color,
            outline=outline_color,
            width=outline_widht,
        )
        button_canvas.addtag_withtag("button", oval2_out)
        button_canvas.addtag_withtag("button", oval2)
        items.append(oval2)
    else:
        rectne = button_canvas.create_rectangle(
            x + lenght - (2 * radius),
            y,
            x + lenght,
            y + (radius * 2),
            fill=fill_color,
            outline="",
        )
        items.append(rectne)
    if corners[2] == 1:
        oval3 = button_canvas.create_arc(
            x,
            y + height,
            x + (radius * 2),
            y + height - (2 * radius),
            start=180,
            extent=90,
            style=tk.PIESLICE,
            fill=fill_color,
            outline="",
        )  # sol alt oval
        oval3_out = button_canvas.create_arc(
            x,
            y + height,
            x + (radius * 2),
            y + height - (2 * radius),
            start=180,
            extent=90,
            style=tk.ARC,
            fill=fill_color,
            outline=outline_color,
            width=outline_widht,
        )  # sol alt oval
        button_canvas.addtag_withtag("button", oval3_out)
        button_canvas.addtag_withtag("button", oval3)
        items.append(oval3)
    else:
        rectsw = button_canvas.create_rectangle(
            x,
            y + height + 1,
            x + (radius * 2),
            y + height - (2 * radius),
            fill=fill_color,
            outline="",
        )
        items.append(rectsw)
    if corners[3] == 1:
        oval4 = button_canvas.create_arc(
            x + lenght - (2 * radius) - 1,
            y + height,
            x + lenght - 1,
            y + height - (2 * radius),
            start=270,
            extent=90,
            style=tk.PIESLICE,
            fill=fill_color,
            outline="",
        )  # sag alt oval
        oval4_out = button_canvas.create_arc(
            x + lenght - (2 * radius) - 1,
            y + height,
            x + lenght - 1,
            y + height - (2 * radius),
            start=270,
            extent=90,
            style=tk.ARC,
            fill=fill_color,
            outline=outline_color,
            width=outline_widht,
        )  # sag alt oval
        button_canvas.addtag_withtag("button", oval4_out)
        button_canvas.addtag_withtag("button", oval4)
        items.append(oval4)
    else:
        rectse = button_canvas.create_rectangle(
            x + lenght - (2 * radius),
            y + height + 1,
            x + lenght,
            y + height - (2 * radius),
            fill=fill_color,
            outline="",
        )
        items.append(rectse)
    # Dikdörtgenin üst ve alt kenarlarını çiz
    rectangle = button_canvas.create_rectangle(
        x + radius, y, x + lenght - radius, y + height + 1, outline="", fill=fill_color
    )
    line1 = button_canvas.create_line(
        x + radius, y, x + lenght - radius, y, fill=outline_color, width=outline_widht
    )  # Üst kenar
    line2 = button_canvas.create_line(
        x + radius,
        y + height,
        x + lenght - radius,
        y + height,
        fill=outline_color,
        width=outline_widht,
    )  # Alt kenar

    rectangle_horizontal = button_canvas.create_rectangle(
        x, y + radius, x + lenght, y + height - radius, fill=fill_color, outline=""
    )
    line3 = button_canvas.create_line(
        x, y + radius, x, y + height - radius, fill=outline_color, width=outline_widht
    )  # Sol kenar
    line4 = button_canvas.create_line(
        x + lenght,
        y + radius,
        x + lenght,
        y + height - radius,
        fill=outline_color,
        width=outline_widht,
    )  # Sag kenar

    button_canvas.addtag_withtag("button", rectangle)
    button_canvas.addtag_withtag("button", line1)
    button_canvas.addtag_withtag("button", line2)
    button_canvas.addtag_withtag("button", rectangle_horizontal)
    button_canvas.addtag_withtag("button", line3)
    button_canvas.addtag_withtag("button", line4)

    items.append(rectangle)
    items.append(rectangle_horizontal)

    def on_enter(e):

        for item in button_canvas.find_all():
            if item in items:
                button_canvas.itemconfig(item, fill=onenter_color)

    def on_leave(e):
        for item in button_canvas.find_all():
            if item in items:
                button_canvas.itemconfig(item, fill=fill_color)

    def start_function(fonksiyon, args):
        return fonksiyon(*args)

    def on_button_click(e):
        start_function(fonksiyon, args)
        for i in button_canvas.find_all():
            if i in items:
                button_canvas.itemconfig(i, fill=active_color)
        button_canvas.itemconfig(text_widget, fill=active_text_color)

    def on_button_release(e):
        for i in button_canvas.find_all():
            if i in items:
                button_canvas.itemconfig(i, fill=fill_color)

        button_canvas.itemconfig(text_widget, fill=text_color)

    # button_canvas.create_rectangle(x-rectangle_lenght, y-radius, x+rectangle_lenght, y+radius, fill="lightblue", outline="black")
    # Buton metnini ekle
    text_widget = button_canvas.create_text(
        x + (lenght / 2), y + (height / 2), text=text, font=font, fill=text_color
    )

    button_canvas.addtag_withtag("button", text_widget)
    button_canvas.tag_bind("button", "<Button-1>", on_button_click)
    button_canvas.tag_bind("button", "<ButtonRelease-1>", on_button_release)
    button_canvas.tag_bind("button", "<Enter>", on_enter)
    button_canvas.tag_bind("button", "<Leave>", on_leave)
    return button_canvas
