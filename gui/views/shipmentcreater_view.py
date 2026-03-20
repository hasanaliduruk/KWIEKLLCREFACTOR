import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread
import os

from utils.file_operations import (
    browse_directory,
    placeholder_saver,
    path_text_function,
    write_settings,
    save_location_saver,
)
from utils.event_handlers import (
    on_focus_in,
    on_focus_out,
    on_click_outside,
    on_mouse_wheel,
    on_text_enter,
    on_text_leave,
)
from utils.gui_helpers import text_print, open_folder_in_explorer, width_f
from gui.components.custom_buttons import MyButton
from gui.components.scrollbar import MyScrollbar
from gui.components.drag_drop import drag_drop
from core.shipment_creator import process_shipment_creation

shipment_settings_var = (
    "RESTOCK:\n"
    "upc = Upc\n"
    "pcs = PCS\n"
    "asin = ASIN\n"
    "pk = PK\n"
    "price = Price\n"
    "suplier = suplier\n"
    "=====================================================\n"
    "ORDER FORM:\n"
    "upc = UPC\n"
    "pcs = PCS\n"
    "asin = ASIN 1, ASIN 2, ASIN 3, ASIN 4\n"
    "SKU = ASIN1_SKU, ASIN2_SKU, ASIN3_SKU, ASIN4_SKU\n"
    "pk = PK\n"
    "price = price\n"
    "suplier = suplier\n"
    "=====================================================\n"
    "INVOICE:\n"
    "shipquantity = ShipQuantity\n"
    "upc = Upc\n"
    "price = NetEach2\n"
    "packsize = PackSize\n"
    "brand = Brand\n"
    "description = Description\n"
)


def shipmentCreater(
    canvas,
    canvas2,
    window,
    color,
    line_color,
    canvas2_text_color,
    dosyalar_dictionary,
    main_frame_resize,
    resize_dictionary,
):
    # MOUSE SCROLL
    def on_mouse_wheel(event):
        canvas2.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # SCROLLBAR VE FRAME OLUSUMU
    shipment_inner_frame = Frame(canvas2, width=0, height=0, bg=color)
    canvas2.create_window((0, 0), anchor="nw", window=shipment_inner_frame)
    shipment_scrollbar_y = MyScrollbar(
        window,
        target=canvas2,
        command=canvas2.yview,
        thumb_thickness=8,
        thumb_color="#888888",
        thickness=18,
        line_color=line_color,
    )
    canvas2.configure(yscrollcommand=shipment_scrollbar_y.set)
    shipment_scrollbar_y.pack(side=RIGHT, fill=tk.Y)

    # INNER FRAME GRID SETTINGS
    shipment_inner_frame.grid_propagate(False)
    shipment_inner_frame.grid_columnconfigure(0, weight=1)

    # OGELERI GURUPLAMAK ICIN CANVAS OLUSUMU

    title_canvas = Canvas(shipment_inner_frame, bg=color, highlightthickness=0)
    title_canvas.grid(column=0, row=0, sticky="nwes")
    items_canvas = Canvas(shipment_inner_frame, bg=color, highlightthickness=0)

    items_canvas.grid(column=0, row=1, sticky="nwes")

    title_canvas.grid_columnconfigure(0, weight=1)
    items_canvas.grid_columnconfigure(0, weight=1)
    # CANVASLAR ICINEKI OGELERIN OLUSUMU

    Shipment_Title = Label(
        title_canvas,
        text="Shipment Creater",
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
    save_name_label = Label(
        title_canvas,
        text="Aşağıya sonucun kaydedilmesini istediginiz ismi giriniz:",
        background=color,
        font=("JetBrainsMonoRoman Regular", 12),
        fg=canvas2_text_color,
    )
    save_name_text = Text(
        title_canvas,
        height=1,
        border=0,
        fg=canvas2_text_color,
        bg=line_color,
        font=("JetBrainsMonoRoman Regular", 12),
        pady=4,
        insertbackground="#c0c0c0",
    )
    dc_name_label = Label(
        title_canvas,
        text="DC KODU:",
        background=color,
        font=("JetBrainsMonoRoman Regular", 12),
        fg=canvas2_text_color,
    )
    dc_name_text = Text(
        title_canvas,
        height=1,
        border=0,
        fg=canvas2_text_color,
        bg=line_color,
        font=("JetBrainsMonoRoman Regular", 12),
        pady=4,
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
    if "shipment_settings.txt" not in os.listdir("Settings"):
        write_settings("Settings/shipment_settings.txt", shipment_settings_var)
    shipment_settings = Text(
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
    shipment_settings.bind("<Enter>", lambda e: on_text_enter(e, canvas2))
    shipment_settings.bind("<Leave>", lambda e: on_text_leave(e, canvas2))
    with open("Settings/shipment_settings.txt", "r", encoding="utf-8") as file:
        readed = file.read()
        shipment_settings.insert(tk.END, readed)
        shipment_settings.see(tk.END)

    def browse_click(event, c, t, text_item, b):
        browse_color_change(event, c, t, b)
        browse_directory(text_item, w=window)

    def browse_color_change(e, c, t, b):
        b.config(background=c, text_color=t)

    def save_click(event, c, t, b):
        browse_color_change(event, c, t, b)
        placeholder_saver("shi", path_text)

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

    browse_button.pack(side=RIGHT, fill=tk.Y, padx=(8, 0))
    save_button.pack(side=RIGHT, fill=tk.Y, padx=(8, 0))
    path_text.pack(side=LEFT, fill=X, expand=True, padx=0, pady=0)
    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function("shi", path_text, placeholder, save_name_text)
    window.unbind("<Button-1>")
    path_text.bind(
        "<Button-1>",
        lambda e: on_focus_in(e, path_text, placeholder, canvas2_text_color),
    )
    path_text.bind(
        "<FocusOut>",
        lambda e: on_focus_out(e, path_text, placeholder, canvas2_text_color),
    )
    window.bind(
        "<Button-1>",
        lambda e: on_click_outside(e, path_text, placeholder, canvas2_text_color),
    )

    def resize(e, a):
        scale = main_frame_resize()
        items = items_canvas.winfo_children()
        shipment_inner_frame.config(
            width=resize_dictionary[shipment_inner_frame]["width"] * scale
        )
        for item in items:
            if type(item) == Label and item != settings_label:
                item.config(font=("JetBrainsMonoRoman Regular", round(9 * scale)))
            elif type(item) == Frame:
                item.config(height=round(175 * scale))
        k = 20
        if a == 1:
            shipment_output.pack_configure(padx=(canvas.winfo_width(), 0))
            shipment_output_line.pack_configure(padx=(canvas.winfo_width(), 0))
            k = 300
        p = items_canvas.winfo_y() + items_canvas.winfo_height() + k
        if p >= canvas2.winfo_height():
            shipment_inner_frame.config(height=p)
        else:
            shipment_inner_frame.config(height=canvas2.winfo_height())

    def output(path):
        shipment_output.pack(side=tk.BOTTOM, fill=tk.X, padx=(canvas.winfo_width(), 0))
        shipment_output_line.pack(
            side=tk.BOTTOM, fill=tk.X, padx=(canvas.winfo_width(), 0)
        )

        shipment_ayarlar = shipment_settings.get("1.0", tk.END).rstrip("\n")
        write_settings("Settings/shipment_settings.txt", shipment_ayarlar)
        save_name = save_name_text.get("1.0", tk.END).strip("\n")
        save_location_saver("shi", save_name_text)
        dc_name = dc_name_text.get("1.0", tk.END).strip("\n")

        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(
                shipment_output,
                "Hata: Dosya yolu algılanamadı, lütfen geçerli bir klasör seçin.",
                color="red",
            )
            return
        if dc_name == "":
            text_print(
                shipment_output, "Hata: DC kod değeri algılanamadı.", color="red"
            )
            return

        inv_files = dosyalar_dictionary.get("invoice", [])
        ord_files = dosyalar_dictionary.get("order_form", [])
        res_files = dosyalar_dictionary.get("restock", [])

        def update_progress(msg: str):
            shipment_output.after(0, lambda: text_print(shipment_output, msg))

        def run_in_thread():
            try:
                result = process_shipment_creation(
                    invoice_files=inv_files,
                    order_form_files=ord_files,
                    restock_files=res_files,
                    output_folder=path,
                    save_name=save_name,
                    dc_code=dc_name,
                    settings_content=shipment_ayarlar,
                    progress_callback=update_progress,
                )
                shipment_output.after(
                    0,
                    lambda: text_print(
                        shipment_output, result["message"], color="#90EE90"
                    ),
                )
                shipment_output.after(
                    0, lambda: open_folder_in_explorer(result["output_path"])
                )
            except Exception as e:
                shipment_output.after(
                    0,
                    lambda: text_print(shipment_output, f"Hata: {str(e)}", color="red"),
                )

        conversion_thread = Thread(target=run_in_thread, daemon=True)
        conversion_thread.start()

        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: resize(e, True))

    shipment_submit_button = MyButton(
        items_canvas,
        round=15,
        width=100,
        height=50,
        text="Başlat",
        background=line_color,
        text_color="white",
        align_text="center",
    )

    def color_change(e, c, t):
        shipment_submit_button.config(background=c, text_color=t)

    def shipment_submit_click(e, c, t):
        shipment_submit_button.config(background=c, text_color=t)
        path = path_text.get(1.0, tk.END)
        path = path.strip("\n")
        output(path)

    shipment_submit_button.bind(
        "<Button-1>", lambda e: shipment_submit_click(e, "#8AB4F8", "black")
    )
    shipment_submit_button.bind(
        "<ButtonRelease-1>", lambda e: color_change(e, "#727478", "white")
    )
    shipment_submit_button.bind(
        "<Enter>", lambda e: color_change(e, "#727478", canvas2_text_color)
    )
    shipment_submit_button.bind(
        "<Leave>", lambda e: color_change(e, line_color, "white")
    )

    # YERLESIM

    Shipment_Title.grid(column=0, row=0, sticky="w", padx=(25, 0), pady=(25, 0))
    title_line.grid(column=0, row=1, sticky="we", padx=(20, 0))
    path_label.grid(column=0, row=2, pady=(20, 0), padx=(25, 0), sticky="w")
    path_frame.grid(column=0, row=3, pady=(0, 20), padx=(25, 5), sticky="we")
    save_name_label.grid(column=0, row=4, pady=(0, 0), padx=(25, 0), sticky="w")
    save_name_text.grid(column=0, row=5, pady=(0, 20), padx=(25, 5), sticky="we")
    dc_name_label.grid(column=0, row=6, pady=(0, 0), padx=(25, 0), sticky="w")
    dc_name_text.grid(column=0, row=7, pady=(0, 20), padx=(25, 5), sticky="we")
    drag_drop(
        0,
        1,
        0,
        "invoice",
        "Invoice excelini aşağıya sürükleyip bırakın:",
        items_canvas,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    drag_drop(
        2,
        3,
        0,
        "order_form",
        "OrderForm excelini aşağıya sürükleyip bırakın:",
        items_canvas,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    drag_drop(
        4,
        5,
        0,
        "restock",
        "Restock excelini aşağıya sürükleyip bırakın:",
        items_canvas,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    settings_label.grid(column=0, row=6, columnspan=2, sticky="w", padx=25, pady=3)
    shipment_settings.grid(
        column=0,
        row=7,
        sticky="we",
        padx=25,
        pady=4,
    )
    shipment_submit_button.grid(column=0, row=8, sticky="e", padx=(0, 25), pady=(25, 0))

    # KUTUPHANEYE EKLEME
    canvas2.update_idletasks()
    resize_dictionary[shipment_inner_frame] = {
        "width": 750,
        "height": shipment_inner_frame.winfo_height(),
    }

    # RESIZE
    p = items_canvas.winfo_y() + items_canvas.winfo_height() + 20
    if p >= canvas2.winfo_height():
        shipment_inner_frame.config(height=p)
    else:
        shipment_inner_frame.config(height=canvas2.winfo_height())

    canvas2.bind_all("<MouseWheel>", on_mouse_wheel)
    shipment_inner_frame.bind(
        "<Configure>", lambda e: canvas2.config(scrollregion=canvas2.bbox("all"))
    )
    resize(1, 0)
    window.bind("<Configure>", lambda e: resize(e, 0))
