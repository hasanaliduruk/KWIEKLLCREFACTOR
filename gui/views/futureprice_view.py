import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread

from utils.file_operations import (
    browse_directory,
    placeholder_saver,
    path_text_function,
    write_settings,
    relative_to_assets,
)
from utils.event_handlers import (
    on_focus_in,
    on_focus_out,
    on_click_outside,
    on_mouse_wheel,
    on_text_enter,
    on_text_leave,
)
from utils.gui_helpers import text_print, open_folder_in_explorer
from gui.components.custom_buttons import MyButton
from gui.components.drag_drop import drag_drop, ham_drag_drop2
from core.future_price_updater import process_future_price


def render_futureprice_view(
    future_price_button,
    canvas2,
    window,
    color,
    line_color,
    canvas2_text_color,
    dosyalar_dictionary,
):
    canvas2.unbind_all("<MouseWheel>")

    def color_change(e, c, t, b):
        b.config(background=c, text_color=t)

    color_change(1, "#8AB4F8", "black", future_price_button)
    f_window = tk.Toplevel(window)
    f_window.title("Future Price")
    f_window.geometry("1000x860")
    f_window.config(bg=color)
    # f_window = TkinterDnD.Tk()
    try:
        f_window.iconbitmap("assets/icon.ico")
    except:
        pass
    content_canvas = Canvas(
        f_window,
        bg=color,
        border=0,
        highlightthickness=0,
    )
    content_canvas.place(x=0, y=0)
    content_canvas.grid_columnconfigure(0, weight=1)
    top_frame = Frame(
        content_canvas,
        background=color,
    )
    bottom_frame = Frame(
        content_canvas,
        background=color,
    )
    title = Label(
        top_frame,
        fg=canvas2_text_color,
        bg=color,
        text="Future Price",
        font=("JetBrainsMonoRoman Regular", 24 * -1),
    )
    title_line = Frame(top_frame, bg=line_color, height=2)
    save_path_label = Label(
        top_frame,
        background=color,
        fg=canvas2_text_color,
        text="Sonuçların kaydedilmesini istediğiniz klasörün yolunu giriniz:",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    path_frame = Frame(top_frame, background=color, height=30)
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
    save_name_label = Label(
        top_frame,
        text="Aşağıya sonucun kaydedilmesini istediginiz ismi giriniz:",
        background=color,
        font=("JetBrainsMonoRoman Regular", 12),
        fg=canvas2_text_color,
    )
    save_name_text = Text(
        top_frame,
        height=1,
        border=0,
        fg=canvas2_text_color,
        bg=line_color,
        font=("JetBrainsMonoRoman Regular", 12),
        pady=4,
        insertbackground="#c0c0c0",
    )
    baslat_button = MyButton(
        bottom_frame,
        round=12,
        width=100,
        height=40,
        text="Başlat",
        background=line_color,
        text_color="white",
        align_text="center",
    )
    output_text = Text(
        f_window,
        border=0,
        wrap=WORD,
        bg=line_color,
        fg="#c0c0c0",
        height=10,
        font=("JetBrainsMonoRoman Regular", 13),
        insertbackground="#c0c0c0",
    )

    def browse_click(event, c, t, text_item, b):
        browse_color_change(event, c, t, b)
        browse_directory(text_item, w=f_window)

    def browse_color_change(e, c, t, b):
        b.config(background=c, text_color=t)

    def save_click(event, c, t, b):
        browse_color_change(event, c, t, b)
        placeholder_saver("ftr", save_path)

    def baslat_click(event, c, t, b):
        browse_color_change(event, c, t, b)
        path = save_path.get(1.0, tk.END)
        name = save_name_text.get(1.0, tk.END)
        path = path.strip("\n")
        name = name.strip("\n")
        output(path, name)

    def output(path, name):
        output_text.pack(side=tk.BOTTOM, fill=tk.X, anchor="w")

        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(
                output_text,
                "Hata: Dosya yolu algılanamadı! Doğru bir kayıt klasörü seçtiğinizden emin olun.",
                color="red",
            )
            return

        future_restock = dosyalar_dictionary.get("future_restock", [])
        future_future = dosyalar_dictionary.get("future_future", [])

        if not future_restock or not future_future:
            text_print(
                output_text,
                "Hata: Gerekli (Restock veya Future) Excel dosyalarından biri eksik. Lütfen dosyaları sürükleyin.",
                color="red",
            )
            return

        def update_progress(msg: str):
            output_text.after(0, lambda: text_print(output_text, msg))

        def run_in_thread():
            try:
                result = process_future_price(
                    path=path,
                    name=name,
                    restock_excel=future_restock[0],
                    future_excel=future_future[0],
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
    baslat_button.bind(
        "<Button-1>", lambda e: baslat_click(e, "#8AB4F8", "black", baslat_button)
    )
    baslat_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", baslat_button),
    )
    baslat_button.bind(
        "<Enter>",
        lambda e: browse_color_change(e, "#727478", canvas2_text_color, baslat_button),
    )
    baslat_button.bind(
        "<Leave>", lambda e: browse_color_change(e, line_color, "white", baslat_button)
    )

    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function("ftr", save_path, placeholder, save_name_text)
    f_window.unbind("<Button-1>")
    save_path.bind(
        "<Button-1>",
        lambda e: on_focus_in(e, save_path, placeholder, canvas2_text_color),
    )
    save_path.bind(
        "<FocusOut>",
        lambda e: on_focus_out(e, save_path, placeholder, canvas2_text_color),
    )
    f_window.bind(
        "<Button-1>",
        lambda e: on_click_outside(e, save_path, placeholder, canvas2_text_color),
    )

    browse_button.pack(side=RIGHT, padx=(8, 0))
    save_button.pack(side=RIGHT, padx=(8, 0))
    save_path.pack(side=LEFT, fill=X, expand=True)

    top_frame.grid(column=0, row=0, sticky="we", padx=(25, 0), pady=(25, 0))
    bottom_frame.grid(column=0, row=1, sticky="we", padx=(25, 0))
    top_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(0, weight=1)
    title.grid(column=0, row=0, sticky="w")
    title_line.grid(column=0, row=1, sticky="we")
    save_path_label.grid(column=0, row=2, sticky="w")
    path_frame.grid(column=0, row=3, sticky="we")
    save_name_label.grid(column=0, row=4, sticky="w")
    save_name_text.grid(column=0, row=5, sticky="we")
    return_items_res = drag_drop(
        row1=6,
        row=7,
        column=0,
        dict_name="future_restock",
        text="Restock excel dosyasini asagiya surukleyip birakiniz:",
        parent=bottom_frame,
        padx=0,
        pady=0,
        win=f_window,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    return_items_ftr = drag_drop(
        row1=8,
        row=9,
        column=0,
        dict_name="future_future",
        text="Future Price excel dosyasini asagiya surukleyip birakiniz:",
        parent=bottom_frame,
        padx=0,
        pady=0,
        win=f_window,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    baslat_button.grid(column=0, row=10, sticky="e", pady=(10, 0))

    def on_close():
        canvas2.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas2))
        f_window.destroy()

    f_window.protocol("WM_DELETE_WINDOW", on_close)
    f_window.mainloop()
