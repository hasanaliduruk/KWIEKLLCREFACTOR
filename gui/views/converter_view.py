import tkinter as tk
from tkinter import (
    Canvas,
    Frame,
    Label,
    Text,
    PhotoImage,
    StringVar,
    WORD,
    X,
    RIGHT,
    LEFT,
)
from threading import Thread

from utils.file_operations import (
    browse_directory,
    placeholder_saver,
    path_text_function,
    relative_to_assets,
)
from utils.event_handlers import (
    on_focus_in,
    on_focus_out,
    on_click_outside,
    on_mouse_wheel,
)
from utils.gui_helpers import text_print, open_folder_in_explorer
from gui.components.drag_drop import drag_drop
from gui.components.custom_buttons import MyButton
from gui.components.scrollbar import MyScrollbar
from gui.components.choosers import ConvertChooser
from core.converter import process_conversion


def render_converter_view(
    canvas,
    canvas2,
    main_frame_resize,
    window,
    color,
    line_color,
    canvas2_text_color,
    dosyalar_dictionary,
):
    csv_drag_drop_image = tk.PhotoImage(file=relative_to_assets("csv_drag_drop_rs.png"))
    csv_icon_image = tk.PhotoImage(file=relative_to_assets("csv_icon_rs.png"))
    txt_drag_drop_image = tk.PhotoImage(file=relative_to_assets("txt_drag_drop_rs.png"))
    txt_icon_image = tk.PhotoImage(file=relative_to_assets("txt_icon_rs.png"))

    def resize_converter(e, a):
        scale = main_frame_resize()
        for item in bottom_canvas.winfo_children():
            if type(item) == Frame:
                item.config(height=175 * scale)
        height = bottom_canvas.winfo_y() + bottom_canvas.winfo_height() + 20
        if a:
            convert_output_text.pack_configure(padx=(canvas.winfo_width(), 0))
            if height < canvas2.winfo_height() - 200:
                converter_main_frame.config(
                    width=750 * scale, height=canvas2.winfo_height()
                )
            else:
                converter_main_frame.config(width=750 * scale, height=height + 200)
        else:
            if height < canvas2.winfo_height():
                converter_main_frame.config(
                    width=750 * scale, height=canvas2.winfo_height()
                )
            else:
                converter_main_frame.config(width=750 * scale, height=height)
        canvas2.config(scrollregion=canvas2.bbox("all"))

    converter_main_frame = Frame(
        canvas2, background=color, width=750, height=canvas2.winfo_height()
    )
    canvas2.create_window((0, 0), window=converter_main_frame, anchor="nw")
    canvas2.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas2))
    converter_scrollbar = MyScrollbar(
        window,
        target=canvas2,
        command=canvas2.yview,
        thumb_thickness=8,
        thumb_color="#888888",
        thickness=18,
        line_color=line_color,
    )
    canvas2.config(
        yscrollcommand=converter_scrollbar.set, scrollregion=canvas2.bbox("all")
    )
    converter_scrollbar.pack(side=RIGHT, fill=tk.Y)

    converter_main_frame.grid_columnconfigure(0, weight=1)
    converter_main_frame.grid_propagate(False)

    # creating the top and bottom canvas:

    top_canvas = Canvas(
        converter_main_frame, background=color, highlightthickness=0, border=0
    )
    bottom_canvas = Canvas(
        converter_main_frame, background=color, highlightthickness=0, border=0
    )

    # top and bottom canvaslarin yerlesimi:

    top_canvas.grid(column=0, row=0, sticky="ew", padx=(25, 0), pady=(20, 0))
    top_canvas.grid_columnconfigure(0, weight=1)
    bottom_canvas.grid(column=0, row=1, sticky="ew", padx=(25, 0), pady=0)

    # widgets:

    title = Label(
        top_canvas,
        background=color,
        fg=canvas2_text_color,
        text="Converter",
        font=(("JetBrainsMonoRoman Regular", 24 * -1)),
    )
    title_line = Frame(
        top_canvas,
        height=2,
        background=line_color,
    )
    down_arrow = PhotoImage(file=relative_to_assets("arrow_down1.png"))
    var1 = StringVar()
    var1.set("csv")
    var2 = StringVar()
    var2.set("xlsx")
    convert_choose_frame = ConvertChooser(window, top_canvas, down_arrow, var1, var2)

    def var1_changed(*args):
        items = bottom_canvas.winfo_children()
        for item in items:
            if item != convert_button.canvas:
                item.destroy()
        file_type_dictionary = {
            ".csv": {"bg_image": csv_drag_drop_image, "file_image": csv_icon_image},
            ".xlsx": {"bg_image": 0, "file_image": 0},
            ".txt": {"bg_image": txt_drag_drop_image, "file_image": txt_icon_image},
        }
        file_type = "." + var1.get()
        bg_image = file_type_dictionary[file_type]["bg_image"]
        file_image = file_type_dictionary[file_type]["file_image"]
        drag_drop(
            0,
            1,
            0,
            "convert",
            "Aşağıya dönüştürmek istediğiniz dosyaları sürükleyip bırakınız:",
            bottom_canvas,
            padx=0,
            bg_image=bg_image,
            file_image=file_image,
            file_type=file_type,
            window=window,
            canvas2=canvas2,
            color=color,
            text_color=canvas2_text_color,
            dosyalar_dictionary=dosyalar_dictionary,
        )
        """if var1.get() == 'csv':
            drag_drop(0,1,0,'convert',
                      'Aşağıya dönüştürmek istediğiniz dosyaları sürükleyip bırakınız:',
                      bottom_canvas, padx=0, bg_image=csv_drag_drop_image, file_image=csv_icon_image, file_type=".csv",
                      window=window, canvas2=canvas2, color=color, text_color=canvas2_text_color, dosyalar_dictionary=dosyalar_dictionary)
        elif var1.get() == 'xlsx':
            drag_drop(0,1,0,'convert',
                      'Aşağıya dönüştürmek istediğiniz dosyaları sürükleyip bırakınız:',
                      bottom_canvas, padx=0, file_type=".xlsx",
                      window=window, canvas2=canvas2, color=color, text_color=canvas2_text_color, dosyalar_dictionary=dosyalar_dictionary)"""

    var1.trace_add("write", var1_changed)

    save_path_label = Label(
        top_canvas,
        background=color,
        fg=canvas2_text_color,
        text="Sonuçların kaydedilmesini istediğiniz klasörün yolunu giriniz:",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    path_frame = Frame(top_canvas, background=color, height=30)
    save_path = Text(
        path_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg="#747474",
        background=line_color,
        border=0,
        pady=4,
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

    def browse_click(event, c, t, text_item, b):
        browse_color_change(event, c, t, b)
        browse_directory(text_item, w=window)

    def browse_color_change(e, c, t, b):
        b.config(background=c, text_color=t)

    def save_click(event, c, t, b):
        browse_color_change(event, c, t, b)
        placeholder_saver("converter", save_path)

    browse_button.bind(
        "<Button-1>",
        lambda e: browse_click(e, "#8AB4F8", "black", save_path, browse_button),
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
    bottom_canvas.grid_columnconfigure(0, weight=1)

    converter_return = drag_drop(
        0,
        1,
        0,
        "convert",
        "Aşağıya dönüştürmek istediğiniz dosyaları sürükleyip bırakınız:",
        bottom_canvas,
        padx=0,
        bg_image=csv_drag_drop_image,
        file_image=csv_icon_image,
        file_type=".csv",
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    converter_dd_text = converter_return[0]
    converter_dd_frame = converter_return[1]
    convert_button = MyButton(
        bottom_canvas,
        round=15,
        width=100,
        height=50,
        text="Dönüştür",
        background=line_color,
        text_color="white",
        align_text="center",
    )

    def convert_color_change(e, c, t):
        convert_button.config(background=c, text_color=t)

    def convert_click(e, c, t):
        convert_color_change(e, c, t)
        path = save_path.get(1.0, tk.END)
        path = path.strip("\n")
        input_type = var1.get()
        output_type = var2.get()
        output(path, input_type, output_type)

    convert_button.bind("<Button-1>", lambda e: convert_click(e, "#8AB4F8", "black"))
    convert_button.bind(
        "<ButtonRelease-1>", lambda e: convert_color_change(e, "#727478", "white")
    )
    convert_button.bind(
        "<Enter>", lambda e: convert_color_change(e, "#727478", canvas2_text_color)
    )
    convert_button.bind(
        "<Leave>", lambda e: convert_color_change(e, line_color, "white")
    )

    convert_output_text = Text(
        window,
        border=0,
        wrap=WORD,
        bg=line_color,
        fg="#c0c0c0",
        height=10,
        font=("JetBrainsMonoRoman Regular", 13),
        insertbackground="#c0c0c0",
    )
    # yerlesim:

    title.grid(column=0, row=0, sticky="w")
    title_line.grid(column=0, row=1, sticky="ew")
    convert_choose_frame.grid(column=0, row=2, sticky="ew")
    save_path_label.grid(column=0, row=3, sticky="w", pady=(0, 0))
    path_frame.grid(column=0, row=4, sticky="we")
    browse_button.pack(side=RIGHT, padx=(8, 0))
    save_button.pack(side=RIGHT, padx=(8, 0))
    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function("converter", save_path, placeholder)
    window.unbind("<Button-1>")
    save_path.bind(
        "<Button-1>",
        lambda e: on_focus_in(e, save_path, placeholder, canvas2_text_color),
    )
    save_path.bind(
        "<FocusOut>",
        lambda e: on_focus_out(e, save_path, placeholder, canvas2_text_color),
    )
    window.bind(
        "<Button-1>",
        lambda e: on_click_outside(e, save_path, placeholder, canvas2_text_color),
    )
    save_path.pack(side=LEFT, fill=X, expand=True)
    convert_button.grid(column=0, row=2, sticky="e", padx=0, pady=(15, 0))

    def output(path, input_type, output_type):
        convert_output_text.pack(
            side=tk.BOTTOM, fill=tk.X, padx=(canvas.winfo_width(), 0)
        )
        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: resize_converter(e, True))

        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(
                convert_output_text,
                "Hata: Geçerli bir kayıt yolu seçilmedi.",
                color="red",
            )
            return

        files_to_convert = dosyalar_dictionary.get("convert", [])
        if not files_to_convert:
            text_print(
                convert_output_text,
                "Hata: Dönüştürülecek dosya sürüklemediniz.",
                color="red",
            )
            return

        def update_progress(msg: str):
            convert_output_text.after(0, lambda: text_print(convert_output_text, msg))

        def run_in_thread():
            try:
                result = process_conversion(
                    files_to_convert,
                    path,
                    input_type,
                    output_type,
                    progress_callback=update_progress,
                )
                convert_output_text.after(
                    0,
                    lambda: text_print(
                        convert_output_text, result["message"], color="#90EE90"
                    ),
                )
                convert_output_text.after(
                    0, lambda: open_folder_in_explorer(result["output_path"])
                )
            except Exception as e:
                convert_output_text.after(
                    0,
                    lambda: text_print(
                        convert_output_text, f"Hata: {str(e)}", color="red"
                    ),
                )

        conversion_thread = Thread(target=run_in_thread, daemon=True)
        conversion_thread.start()

    window.bind("<Configure>", lambda e: resize_converter(e, False))
