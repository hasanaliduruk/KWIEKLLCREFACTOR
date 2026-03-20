import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, X, RIGHT, LEFT
import os
from threading import Thread

from utils.file_operations import (
    browse_directory,
    placeholder_saver,
    path_text_function,
)
from utils.event_handlers import (
    on_focus_in,
    on_focus_out,
    on_click_outside,
    on_text_enter,
    on_text_leave,
)
from utils.file_operations import write_settings
from utils.gui_helpers import text_print, open_folder_in_explorer, width_f
from gui.components.drag_drop import drag_drop
from gui.components.custom_buttons import MyButton
from gui.components.scrollbar import MyScrollbar
from core.order_creator import process_order_create

ordercreate_settings_var = (
    "RESTOCK:\n"
    "upc = Upc\n"
    "pcs = PCS\n"
    "suplier = suplier\n"
    "notes = Notes\n"
    "=====================================================\n"
    "ORDER FORM:\n"
    "upc = UPC\n"
    "pcs = PCS(TOTAL)\n"
    "suplier = suplier"
)


def render_ordercreate_view(
    canvas,
    canvas2,
    main_frame_resize,
    window,
    color,
    line_color,
    canvas2_text_color,
    dosyalar_dictionary,
    resize_dictionary,
):

    # RESIZE
    def resize(e, a):
        scale = main_frame_resize()
        restock_dragframe.config(height=175 * scale)
        orderform_dragframe.config(height=175 * scale)
        height = items_canvas.winfo_height() + items_canvas.winfo_y() + 20
        if a:
            output_text.pack_configure(padx=(canvas.winfo_width(), 0))
            if height < canvas2.winfo_height() - 200:
                order_inner_frame.config(
                    width=750 * scale, height=canvas2.winfo_height()
                )
            else:
                order_inner_frame.config(width=750 * scale, height=height + 200)
        else:
            if height < canvas2.winfo_height():
                order_inner_frame.config(
                    width=750 * scale, height=canvas2.winfo_height()
                )
            else:
                order_inner_frame.config(width=750 * scale, height=height)
        canvas2.config(scrollregion=canvas2.bbox("all"))

    # MOUSE SCROLL
    def on_mouse_wheel(event):
        canvas2.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # SCROLLBAR VE FRAME OLUSUMU
    order_inner_frame = Frame(canvas2, width=0, height=0, bg=color)
    canvas2.create_window((0, 0), anchor="nw", window=order_inner_frame)
    canvas2.config(scrollregion=canvas2.bbox("all"))
    order_scrollbar_y = MyScrollbar(
        window,
        target=canvas2,
        command=canvas2.yview,
        thumb_thickness=8,
        thumb_color="#888888",
        thickness=18,
        line_color=line_color,
    )
    canvas2.configure(yscrollcommand=order_scrollbar_y.set)
    order_scrollbar_y.pack(side=RIGHT, fill=tk.Y)

    # INNER FRAME GRID SETTINGS
    order_inner_frame.grid_propagate(False)
    order_inner_frame.grid_columnconfigure(0, weight=1)

    # OGELERI GURUPLAMAK ICIN CANVAS OLUSUMU

    title_canvas = Canvas(order_inner_frame, bg=color, highlightthickness=0)
    title_canvas.grid(column=0, row=0, sticky="nwes")
    items_canvas = Canvas(order_inner_frame, bg=color, highlightthickness=0)

    items_canvas.grid(column=0, row=1, sticky="nwes")

    title_canvas.grid_columnconfigure(0, weight=1)
    items_canvas.grid_columnconfigure(0, weight=1)
    # CANVASLAR ICINEKI OGELERIN OLUSUMU

    Order_Title = Label(
        title_canvas,
        text="Order Creater",
        font=("JetBrainsMonoRoman Regular", 24 * -1),
        bg=color,
        fg=canvas2_text_color,
    )
    title_line = Frame(title_canvas, height=2, bg=line_color)
    shipment_output = Text(
        window,
        border=0,
        wrap=WORD,
        bg=line_color,
        fg="#c0c0c0",
        height=10,
        font=("JetBrainsMonoRoman Regular", 13),
        insertbackground="#c0c0c0",
    )
    shipment_output.bind("<Enter>", lambda e: on_text_enter(e, canvas2))
    shipment_output.bind("<Leave>", lambda e: on_text_leave(e, canvas2))
    shipment_output_line = Frame(window, height=2, bg="#787a7e")

    path_label = Label(
        title_canvas,
        text="Aşağıya sonuçların kaydedilmesini istediğiniz dosya yolunu giriniz:",
        background=color,
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12),
    )

    path_frame = Frame(title_canvas, bg=color, height=30)
    path_text = Text(
        path_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg="#747474",
        border=0,
        pady=4,
        bg=line_color,
        insertbackground="#c0c0c0",
    )
    browse_button = MyButton(
        path_frame,
        text="Browse",
        background=line_color,
        text_color="white",
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9),
    )
    save_button = MyButton(
        path_frame,
        text="Kaydet",
        background=line_color,
        text_color="white",
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9),
    )

    restock_return = drag_drop(
        0,
        1,
        0,
        "order_create_restock",
        "RESTOCK excel dosyasini asagiya surukleyip birakiniz.",
        items_canvas,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    orderform_return = drag_drop(
        2,
        3,
        0,
        "order_create_orderform",
        "ORDER FORM excel dosyasini asagiya surukleyip birakiniz.",
        items_canvas,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )

    restock_dragframe = restock_return[0]
    orderform_dragframe = orderform_return[0]
    buttons_frame = Frame(items_canvas, border=0, highlightthickness=0, bg=color)
    baslat_button = MyButton(
        buttons_frame,
        round=12,
        width=100,
        height=40,
        text="Başlat",
        background=line_color,
        text_color="white",
        align_text="center",
    )
    template_location_button = MyButton(
        buttons_frame,
        round=12,
        width=100,
        height=40,
        text="Template",
        background=line_color,
        text_color="white",
        align_text="center",
    )
    output_text = Text(
        window,
        border=0,
        wrap=WORD,
        bg=line_color,
        fg="#c0c0c0",
        height=10,
        font=("JetBrainsMonoRoman Regular", 13),
        insertbackground="#c0c0c0",
    )
    settings_height = 250
    settings_label = Label(
        items_canvas,
        text="Settings:",
        font=("JetBrainsMonoRoman Regular", 12),
        background=color,
        fg=canvas2_text_color,
    )
    if "ordercreate_settings.txt" not in os.listdir("Settings"):
        write_settings("Settings/ordercreate_settings.txt", ordercreate_settings_var)
    order_create_settings = Text(
        items_canvas,
        border=0,
        wrap=WORD,
        width=int(width_f(650, canvas2)),
        bg=line_color,
        fg="#c0c0c0",
        height=int(settings_height / 15),
        font=("JetBrainsMonoRoman Regular", 10),
        insertbackground="#c0c0c0",
    )
    order_create_settings.bind("<Enter>", lambda e: on_text_enter(e, canvas2))
    order_create_settings.bind("<Leave>", lambda e: on_text_leave(e, canvas2))
    with open("Settings/ordercreate_settings.txt", "r", encoding="utf-8") as file:
        readed = file.read()
        order_create_settings.insert(tk.END, readed)
        order_create_settings.see(tk.END)
    items_canvas.grid_columnconfigure(0, weight=1)

    baslat_button.pack(side=RIGHT)
    template_location_button.pack(side=RIGHT, padx=(0, 15))
    buttons_frame.grid(column=0, row=6, padx=(0, 25), pady=(20, 0), sticky="e")
    settings_label.grid(column=0, row=4, columnspan=2, sticky="w", padx=25, pady=3)
    order_create_settings.grid(
        column=0,
        row=5,
        sticky="we",
        padx=25,
        pady=4,
    )

    def browse_click(event, c, t, text_item, b):
        browse_color_change(event, c, t, b)
        browse_directory(text_item, w=window)

    def browse_color_change(e, c, t, b):
        b.config(background=c, text_color=t)

    def save_click(event, c, t, b):
        browse_color_change(event, c, t, b)
        placeholder_saver("order_create", path_text)

    def color_changer(event, c, t, b):
        b.config(background=c, text_color=t)

    def template_location_button_click(event, c, t, b):
        b.config(background=c, text_color=t)
        path = os.getcwd()
        open_folder_in_explorer(f"{path}/Settings/Template")

    def baslat_button_click(event, c, t, b):
        b.config(background=c, text_color=t)
        path = path_text.get(1.0, tk.END).strip()
        maindir = os.getcwd()
        template = f"{maindir}/Settings/Template/Template.xlsx"
        restock_excel = dosyalar_dictionary["order_create_restock"]
        orderform_excel = dosyalar_dictionary["order_create_orderform"]
        output(path, template, restock_excel, orderform_excel)

    browse_button.bind(
        "<Button-1>",
        lambda e: browse_click(e, "#8AB4F8", "black", path_text, browse_button),
    )
    browse_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", browse_button),
    )
    browse_button.bind(
        "<Enter>",
        lambda e: browse_color_change(e, "#727478", canvas2_text_color, browse_button),
    )
    browse_button.bind(
        "<Leave>", lambda e: browse_color_change(e, line_color, "white", browse_button)
    )
    save_button.bind(
        "<Button-1>", lambda e: save_click(e, "#8AB4F8", "black", save_button)
    )
    save_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", save_button),
    )
    save_button.bind(
        "<Enter>",
        lambda e: browse_color_change(e, "#727478", canvas2_text_color, save_button),
    )
    save_button.bind(
        "<Leave>", lambda e: browse_color_change(e, line_color, "white", save_button)
    )
    baslat_button.bind(
        "<Button-1>",
        lambda e: baslat_button_click(e, "#8AB4F8", "black", baslat_button),
    )
    baslat_button.bind(
        "<ButtonRelease-1>",
        lambda e: color_changer(e, "#727478", "white", baslat_button),
    )
    baslat_button.bind(
        "<Enter>",
        lambda e: color_changer(e, "#727478", canvas2_text_color, baslat_button),
    )
    baslat_button.bind(
        "<Leave>", lambda e: color_changer(e, line_color, "white", baslat_button)
    )
    template_location_button.bind(
        "<Button-1>",
        lambda e: template_location_button_click(
            e, "#8AB4F8", "black", template_location_button
        ),
    )
    template_location_button.bind(
        "<ButtonRelease-1>",
        lambda e: color_changer(e, "#727478", "white", template_location_button),
    )
    template_location_button.bind(
        "<Enter>",
        lambda e: color_changer(
            e, "#727478", canvas2_text_color, template_location_button
        ),
    )
    template_location_button.bind(
        "<Leave>",
        lambda e: color_changer(e, line_color, "white", template_location_button),
    )

    browse_button.pack(side=RIGHT, fill=tk.Y, padx=(8, 0))
    save_button.pack(side=RIGHT, fill=tk.Y, padx=(8, 0))
    path_text.pack(side=LEFT, fill=X, expand=True, padx=0, pady=0)
    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function("order_create", path_text, placeholder)
    window.unbind("<Button-1>")
    path_text.bind(
        "<Button-1>",
        lambda e: on_focus_in(e, path_text, placeholder, canvas2_text_color),
    )
    path_text.bind(
        "<FocusOut>",
        lambda e: on_focus_out(e, path_text, placeholder, canvas2_text_color),
    )

    canvas2.update_idletasks()
    resize_dictionary[order_inner_frame] = {
        "width": 750,
        "height": order_inner_frame.winfo_height(),
    }

    window.bind(
        "<Button-1>",
        lambda e: on_click_outside(e, path_text, placeholder, canvas2_text_color),
    )

    Order_Title.grid(column=0, row=0, sticky="w", padx=(25, 0), pady=(25, 0))
    title_line.grid(column=0, row=1, sticky="we", padx=(20, 0))
    path_label.grid(column=0, row=2, pady=(20, 0), padx=(25, 0), sticky="w")
    path_frame.grid(column=0, row=3, pady=(0, 20), padx=(25, 5), sticky="we")

    def output(path, template, restock_excel, orderform_excel):
        output_text.pack(side=tk.BOTTOM, fill=tk.X, padx=(canvas.winfo_width(), 0))
        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: resize(e, True))

        ordercreate_ayarlar = order_create_settings.get("1.0", tk.END).rstrip("\n")
        write_settings("Settings/ordercreate_settings.txt", ordercreate_ayarlar)

        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(
                output_text,
                "Hata: Dosya yolu algılanamadı, lütfen geçerli bir klasör seçin.",
                color="red",
            )
            return

        if not restock_excel:
            text_print(
                output_text,
                "Hata: İşlenecek Restock excel dosyası sürüklemediniz.",
                color="red",
            )
            return

        if not orderform_excel:
            text_print(
                output_text,
                "Hata: İşlenecek Order Form excel dosyası sürüklemediniz.",
                color="red",
            )
            return

        def update_progress(msg: str):
            output_text.after(0, lambda: text_print(output_text, msg))

        def run_in_thread():
            try:
                result = process_order_create(
                    restock_files=restock_excel,
                    orderform_files=orderform_excel,
                    template_path=template,
                    output_folder=path,
                    settings_content=ordercreate_ayarlar,
                    progress_callback=update_progress,
                )
                output_text.after(
                    0,
                    lambda: text_print(output_text, result["message"], color="#90EE90"),
                )
                output_text.after(
                    0, lambda: open_folder_in_explorer(result["output_path"])
                )
            except Exception as e:
                output_text.after(
                    0, lambda: text_print(output_text, f"Hata: {str(e)}", color="red")
                )

        conversion_thread = Thread(target=run_in_thread, daemon=True)
        conversion_thread.start()

    canvas2.bind_all("<MouseWheel>", on_mouse_wheel)
    window.bind("<Configure>", lambda e: resize(e, False))
