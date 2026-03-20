"""
This project made by HASAN ALI DURUK
Duruk/'s Software LLC
"""

from utils.gui_helpers import dark_title_bar, silici
from utils.file_operations import relative_to_assets
from utils.event_handlers import button_hover, button_leave
from gui.components.custom_buttons import MyButton
from gui.views.tsv_view import render_tsv_view
from gui.views.expration_view import render_expration_view
from gui.views.costupdater_view import render_costupdater_view
from gui.views.restock_view import render_restock_view
from gui.views.invoice_view import render_invoice_view
from gui.views.converter_view import render_converter_view
from gui.views.invoicefinder_view import render_invoicefinder_view
from gui.views.ordercreate_view import render_ordercreate_view
from gui.views.updater_view import render_updater_view
from gui.views.shipmentcreater_view import shipmentCreater
from core.updater_service import check_internet, get_latest_release
from screeninfo import get_monitors
from tkinter import messagebox
from multiprocessing import freeze_support
from pathlib import Path
from PIL import Image as HASAN
from PIL import ImageTk
from tkinter import *
from tkinter import Canvas, PhotoImage
from tkinterdnd2 import TkinterDnD


def button(canvas2, button):
    canvas2.delete("all")
    canvas2.unbind_all("<MouseWheel>")
    window.unbind("<Configure>")
    silici(canvas, canvas2, window)
    scrollbar = Scrollbar()
    canvas2.config(
        scrollregion=canvas2.bbox("all")
    )  # Canvas'ın scroll bölgesini güncelle
    scrollbar.config(command=canvas2.yview)
    canvas2.config(yscrollcommand=scrollbar.set)
    canvas2.yview_moveto(0)

    image_dictionary = {
        button_1: program_icon_selected,
        button_2: program_icon_selected,
        button_3: program_icon_selected,
        button_4: program_icon_selected,
        button_5: home_icon_selected,
        button_6: program_icon_selected,
        button_7: program_icon_selected,
        button_8: program_icon_selected,
        button_9: program_icon_selected,
        button_10: program_icon_selected,
        button_11: program_icon_selected,
    }
    button_1.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_2.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_3.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_4.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_5.config(
        background=color, text_color=canvas2_text_color, image=home_icon_notselected
    )
    button_6.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_7.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_8.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_9.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_10.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button_11.config(
        background=color, text_color=canvas2_text_color, image=program_icon_notselected
    )
    button.config(
        background="#8AB4F8", text_color="black", image=image_dictionary[button]
    )

    def dictionary_update(button):
        dictionary[button_1] = 0
        dictionary[button_2] = 0
        dictionary[button_3] = 0
        dictionary[button_4] = 0
        dictionary[button_5] = 0
        dictionary[button_6] = 0
        dictionary[button_7] = 0
        dictionary[button_8] = 0
        dictionary[button_9] = 0
        dictionary[button_10] = 0
        dictionary[button_11] = 0
        dictionary[button] = 1

    if button == button_1:
        dictionary_update(button_1)
        canvas2.unbind_all("<MouseWheel>")
        render_expration_view(
            canvas,
            canvas2,
            window,
            color,
            line_color,
            canvas2_text_color,
            main_frame_resize,
        )
    if button == button_2:
        window.unbind("<Configure>")
        dictionary_update(button_2)
        shipmentCreater(
            canvas,
            canvas2,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
            main_frame_resize,
            resize_dictionary,
        )
    if button == button_3:
        dictionary_update(button_3)
        canvas2.unbind_all("<MouseWheel>")
        render_tsv_view(
            canvas,
            canvas2,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
            main_frame_resize,
        )
    if button == button_4:
        dictionary_update(button_4)
        canvas2.config(height=window.winfo_height())
        render_restock_view(
            canvas,
            canvas2,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
            resize_dictionary,
            active_dictionary,
            main_frame_resize,
        )

    if button == button_5:
        dictionary_update(button_5)
        canvas2.unbind_all("<MouseWheel>")

        anasayfa_canvas = Canvas(
            canvas2, background=color, highlightthickness=0, border=0
        )
        anasayfa_canvas.pack(anchor="center", expand=True, side=LEFT)

        line = Frame(anasayfa_canvas, height=4, background=line_color)

        hello = Label(
            anasayfa_canvas,
            background=color,
            fg=canvas2_text_color,
            text="KWIEK LLC TOPLU İŞLEM PLATFORMUNA HOŞGELDİNİZ!",
            font=("JetBrainsMonoRoman Regular", 24 * -1),
        )

        islem = Label(
            anasayfa_canvas,
            background=color,
            text="Bir işlem yapmak için lütfen sol menüdeki işlemlerden birini seçiniz...",
            fg=canvas2_text_color,
            font=("JetBrainsMonoRoman Regular", 15 * -1),
        )

        hello.grid(column=0, row=0, sticky="ew", padx=40)
        line.grid(column=0, row=1, sticky="ew", pady=15)
        islem.grid(column=0, row=2, sticky="ew")
        liste = [canvas, canvas2, button_1, button_2, button_3, button_4, button_5]
        window.bind("<Configure>", lambda e: main_resize(e, liste, hello, islem))
    if button == button_6:

        dictionary_update(button_6)
        canvas2.unbind_all("<MouseWheel>")
        render_invoice_view(
            canvas,
            canvas2,
            main_frame_resize,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
            selected_image,
            not_selected_image,
            csv_drag_drop_image,
            csv_icon_image,
        )
    if button == button_7:
        dictionary_update(button_7)
        render_converter_view(
            canvas,
            canvas2,
            main_frame_resize,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
        )
    if button == button_8:
        dictionary_update(button_8)
        render_costupdater_view(
            canvas,
            canvas2,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
            main_frame_resize,
        )
    if button == button_9:
        dictionary_update(button_9)
        render_updater_view(
            canvas2, color, window, line_color, canvas2_text_color, CURRENT_VERSION
        )
    if button == button_10:
        dictionary_update(button_10)
        render_invoicefinder_view(
            canvas,
            canvas2,
            main_frame_resize,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
        )
    if button == button_11:
        dictionary_update(button_11)
        render_ordercreate_view(
            canvas,
            canvas2,
            main_frame_resize,
            window,
            color,
            line_color,
            canvas2_text_color,
            dosyalar_dictionary,
            resize_dictionary,
        )


if __name__ == "__main__":
    freeze_support()

    CURRENT_VERSION = "v1.2.2"

    OUTPUT_PATH = Path(__file__).resolve().parent
    ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

    dosyalar_dictionary = {}

    color = "#202124"
    window = TkinterDnD.Tk()

    # bg='#ADD8E6'

    canvas2_text_color = "#E3E3E3"
    line_color = "#3F4042"
    active_dictionary = {"restock": 1, "export": 1}

    # 865x519
    wr = float(865 / 1920)
    hr = float(519 / 1080)
    m = get_monitors()[0]

    scale = 1
    window.configure(bg=color)
    screenwidth = int(scale * wr * 2560)
    screen_height = int(scale * hr * 1600)
    # print(screenwidth,screen_height)
    window.geometry("{}x{}".format(screenwidth, screen_height))
    window.title("KWIEK LLC")
    try:
        dark_title_bar(window)
    except:
        pass
    try:
        window.iconbitmap("assets/icon.ico")
    except:
        pass

    original_selected_image = HASAN.open(relative_to_assets("selected.png"))
    original_notselected_image = HASAN.open(relative_to_assets("not_selected.png"))
    selected_resized_image = original_selected_image.resize((15, 15))
    notselected_resized_image = original_notselected_image.resize((15, 15))
    selected_image = ImageTk.PhotoImage(selected_resized_image)
    not_selected_image = ImageTk.PhotoImage(notselected_resized_image)
    csv_drag_drop_image = PhotoImage(file=relative_to_assets("csv_drag_drop_rs.png"))
    csv_icon_image = PhotoImage(file=relative_to_assets("csv_icon_rs.png"))
    txt_drag_drop_image = PhotoImage(file=relative_to_assets("txt_drag_drop_rs.png"))
    txt_icon_image = PhotoImage(file=relative_to_assets("txt_icon_rs.png"))

    global last_scale
    last_scale = 1

    def main_frame_resize():
        global last_scale
        new_width = window.winfo_width()
        new_height = window.winfo_height()
        scale = (new_width * new_height) / (screen_height * screenwidth)
        scale = round(scale, 1)
        if scale <= 1:
            scale = 1
        elif scale >= 1.60:
            scale = 1.60
        canvas.place_configure(height=new_height)
        canvas2.place_configure(
            height=new_height, width=new_width - canvas.winfo_width() + 10
        )
        if scale != last_scale:
            canvas.place_configure(width=resize_dictionary[canvas]["width"] * scale)
            canvas2.place_configure(
                x=resize_dictionary[canvas2]["x"] * scale,
                y=resize_dictionary[canvas2]["y"] * scale,
            )
            button_list = [
                button_1,
                button_2,
                button_3,
                button_4,
                button_5,
                button_6,
                button_7,
                button_8,
                button_9,
                button_10,
                button_11,
            ]
            for button in button_list:
                width = resize_dictionary[button]["width"] * scale
                height = resize_dictionary[button]["height"] * scale
                button.config(width=width, height=height, round=20 * scale)
            last_scale = scale
        return scale

    def main_resize(event, liste, hello, islem):
        scale = main_frame_resize()
        hello.config(font=("JetBrainsMonoRoman Regular", round(24 * scale) * -1))
        islem.config(font=("JetBrainsMonoRoman Regular", round(15 * scale) * -1))

    window.update()

    canvas2_height = 519
    canvas2_width = 763
    canvas_widht = 175
    canvas2 = Canvas(
        window,
        height=int((window.winfo_height())),
        width=int((window.winfo_width() - canvas_widht)),
        bd=0,
        highlightthickness=0,
        relief="ridge",
        background=color,
    )
    canvas2.place(x=int(canvas_widht * scale), y=0)

    canvas2.pack_propagate(False)
    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=int((window.winfo_height())),
        width=int(canvas_widht * scale) + 3,
        border=0,
        bd=0,
        highlightthickness=0,
        relief="ridge",
        background=color,
    )
    canvas.place(x=0, y=0)
    canvas.grid_propagate(False)
    canvas.grid_columnconfigure(0, weight=1)
    canvas.grid_columnconfigure(1, weight=2)

    anasayfa_canvas = Canvas(canvas2, background=color, highlightthickness=0, border=0)
    anasayfa_canvas.pack(anchor="center", expand=True, side=LEFT)

    line = Frame(anasayfa_canvas, height=4, background=line_color)

    hello = Label(
        anasayfa_canvas,
        background=color,
        fg=canvas2_text_color,
        text="KWIEK LLC TOPLU İŞLEM PLATFORMUNA HOŞGELDİNİZ!",
        font=("JetBrainsMonoRoman Regular", 24 * -1),
    )

    islem = Label(
        anasayfa_canvas,
        background=color,
        text="Bir işlem yapmak için lütfen sol menüdeki işlemlerden birini seçiniz...",
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 15 * -1),
    )

    hello.grid(column=0, row=0, sticky="ew", padx=40)
    line.grid(column=0, row=1, sticky="ew", pady=15)
    islem.grid(column=0, row=2, sticky="ew")

    home_icon_selected = PhotoImage(
        file=relative_to_assets("home_icon_selected_rs.png")
    )
    home_icon_hover = PhotoImage(file=relative_to_assets("home_icon_hover_rs.png"))
    home_icon_notselected = PhotoImage(
        file=relative_to_assets("home_icon_notselected_rs.png")
    )
    program_icon_selected = PhotoImage(
        file=relative_to_assets("program_icon_selected_rs.png")
    )
    program_icon_hover = PhotoImage(
        file=relative_to_assets("program_icon_hover_rs.png")
    )
    program_icon_notselected = PhotoImage(
        file=relative_to_assets("program_icon_notselected_rs.png")
    )
    pad = 5
    button_1 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Expration Date",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_1.grid(column=0, row=6)

    button_1.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_1, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_1.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_1,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_1.bind("<Button-1>", lambda e: button(canvas2, button_1))
    button_1_line = Frame(canvas, height=2, bg=line_color)
    button_1_line.grid(column=0, row=7, sticky="ew")
    button_2 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Shipment Creater",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_2.grid(column=0, row=8)
    button_2.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_2, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_2.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_2,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_2.bind("<Button-1>", lambda e: button(canvas2, button_2))
    button_2_line = Frame(canvas, height=2, bg=line_color)
    button_2_line.grid(column=0, row=9, sticky="ew")
    button_3 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="TSV PROGRAMI",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_3.grid(column=0, row=10)
    button_3.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_3, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_3.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_3,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_3.bind("<Button-1>", lambda e: button(canvas2, button_3))
    button_3_line = Frame(canvas, height=2, bg=line_color)
    button_4 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="RESTOCK",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_4.grid(column=0, row=4)
    button_4.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_4, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_4.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_4,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_4.bind("<Button-1>", lambda e: button(canvas2, button_4))
    button_4_line = Frame(canvas, height=2, bg=line_color)
    button_4_line.grid(column=0, row=5, sticky="ew")

    button_5 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color="black",
        text="Ana Sayfa",
        align_text="west",
        round=20,
        background="#8AB4F8",
        corners=[0, 1, 0, 1],
        image=home_icon_selected,
        text_pad=pad,
    )
    button_5.grid(column=0, row=0, pady=(30, 0))
    button_5.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_5, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_5.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_5,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_5.bind("<Button-1>", lambda e: button(canvas2, button_5))
    button_5_line1 = Frame(canvas, height=2, bg=line_color)
    button_5_line2 = Frame(canvas, height=2, bg=line_color)
    button_5_line3 = Frame(canvas, height=2, bg=line_color)
    button_5_line1.grid(column=0, row=1, sticky="ew", pady=(20, 1))
    button_5_line2.grid(column=0, row=2, sticky="ew", pady=(1, 1))
    button_5_line3.grid(column=0, row=3, sticky="ew", pady=(1, 20))

    button_6_line = Frame(canvas, height=2, bg=line_color)
    button_6_line.grid(column=0, row=11, sticky="ew")
    button_6 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Invoice",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_6.grid(column=0, row=12)
    button_6.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_6, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_6.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_6,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_6.bind("<Button-1>", lambda e: button(canvas2, button_6))

    button_7_line = Frame(canvas, height=2, bg=line_color)
    button_7_line.grid(column=0, row=13, sticky="ew")
    button_7 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Converter",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_7.grid(column=0, row=14)
    button_7.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_7, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_7.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_7,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_7.bind("<Button-1>", lambda e: button(canvas2, button_7))

    button_8_line = Frame(canvas, height=2, bg=line_color)
    button_8_line.grid(column=0, row=15, sticky="ew")

    button_8 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Cost Updater",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_8.grid(column=0, row=16)
    button_8.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_8, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_8.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_8,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_8.bind("<Button-1>", lambda e: button(canvas2, button_8))

    button_9_line = Frame(canvas, height=2, bg=line_color)
    button_9_line.grid(column=0, row=21, sticky="ew")
    button_9 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Update",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_9.grid(column=0, row=22)
    button_9.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_9, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_9.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_9,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_9.bind("<Button-1>", lambda e: button(canvas2, button_9))

    button_10_line = Frame(canvas, height=2, bg=line_color)
    button_10_line.grid(column=0, row=17, sticky="ew")
    button_10 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Invoice Finder",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_10.grid(column=0, row=18)
    button_10.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_10, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_10.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_10,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_10.bind("<Button-1>", lambda e: button(canvas2, button_10))

    button_11_line = Frame(canvas, height=2, bg=line_color)
    button_11_line.grid(column=0, row=19, sticky="ew")
    button_11 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Order Create",
        align_text="west",
        round=20,
        background=color,
        corners=[0, 1, 0, 1],
        image=program_icon_notselected,
        text_pad=pad,
    )
    button_11.grid(column=0, row=20)
    button_11.bind(
        "<Enter>",
        lambda event: button_hover(
            event, button_11, dictionary, button_5, program_icon_hover, home_icon_hover
        ),
    )
    button_11.bind(
        "<Leave>",
        lambda event: button_leave(
            event,
            button_11,
            dictionary,
            color,
            button_5,
            program_icon_notselected,
            home_icon_notselected,
        ),
    )
    button_11.bind("<Button-1>", lambda e: button(canvas2, button_11))
    dictionary = {
        button_1: 0,
        button_2: 0,
        button_3: 0,
        button_4: 0,
        button_5: 1,
        button_6: 0,
        button_7: 0,
        button_8: 0,
        button_9: 0,
        button_10: 0,
        button_11: 0,
    }
    version = Label(
        canvas,
        fg=canvas2_text_color,
        bg=color,
        text=CURRENT_VERSION,
        font=("Helvatica", 8),
    )
    version.place(x=0, y=0)

    def check_version_at_startup():
        if check_internet():
            data = get_latest_release()
            if data and data["tag_name"] > CURRENT_VERSION:
                version.config(
                    text=f"{CURRENT_VERSION} yeni version({data['tag_name']}) mevcut!",
                    fg="yellow",
                )
                messagebox.showinfo(
                    "Güncelleme", f"Yeni bir versiyon mevcut: {data['tag_name']}"
                )

    window.after(1000, check_version_at_startup)
    liste = [
        canvas,
        canvas2,
        button_1,
        button_2,
        button_3,
        button_4,
        button_5,
        button_6,
        button_7,
        button_8,
    ]

    window.update_idletasks()
    resize_dictionary = {
        canvas: {
            "width": canvas.winfo_width(),
            "height": canvas.winfo_height(),
            "x": canvas.winfo_x(),
            "y": canvas.winfo_y(),
        },
        canvas2: {
            "width": canvas2.winfo_width(),
            "height": canvas2.winfo_height(),
            "x": canvas2.winfo_x(),
            "y": canvas2.winfo_y(),
        },
        button_1: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_1.winfo_x(),
            "y": button_1.winfo_y(),
        },
        button_2: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_2.winfo_x(),
            "y": button_2.winfo_y(),
        },
        button_3: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_3.winfo_x(),
            "y": button_3.winfo_y(),
        },
        button_4: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_4.winfo_x(),
            "y": button_4.winfo_y(),
        },
        button_5: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_5.winfo_x(),
            "y": button_5.winfo_y(),
        },
        button_6: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_6.winfo_x(),
            "y": button_6.winfo_y(),
        },
        button_7: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_7.winfo_x(),
            "y": button_7.winfo_y(),
        },
        button_8: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_8.winfo_x(),
            "y": button_8.winfo_y(),
        },
        button_9: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_9.winfo_x(),
            "y": button_9.winfo_y(),
        },
        button_10: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_10.winfo_x(),
            "y": button_10.winfo_y(),
        },
        button_11: {
            "width": canvas_widht * scale,
            "height": 45 * scale,
            "x": button_11.winfo_x(),
            "y": button_11.winfo_y(),
        },
    }
    window.bind("<Configure>", lambda e: main_resize(e, liste, hello, islem))
    # 888888
    window.mainloop()
