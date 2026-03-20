import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
import os

from utils.file_operations import (
    browse_directory,
    placeholder_saver,
    path_text_function,
    write_settings,
)
from utils.event_handlers import (
    on_focus_in,
    on_focus_out,
    on_click_outside,
    on_mouse_wheel,
)
from utils.gui_helpers import text_print, open_folder_in_explorer
from gui.components.custom_buttons import MyButton
from gui.components.scrollbar import MyScrollbar
from core.expiration_processor import process_expiration


import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread

expration_settings_var = (
    "login_button_id = mainForm:j_idt23, mainForm:j_idt13\n"
    "email_id = mainForm:email\n"
    "password_id = mainForm:password\n"
    "default_email = sales@buyable.net\n"
    "default_password = hasali2603\n"
)


def render_expration_view(
    canvas, canvas2, window, color, line_color, canvas2_text_color, main_frame_resize
):
    def color_change(e, c, t, b):
        b.config(background=c, text_color=t)

    def baslat_click(e, c, t, b):
        color_change(e, c, t, b)
        baslat_button.pack_forget()
        baslat_button.pack(side=RIGHT, padx=(5, 0))

        path = save_path.get(1.0, tk.END)
        path = path.strip("\n")
        output(path)

    def output(path):
        window.unbind("<Configure>")
        output_text.pack(
            side=BOTTOM, fill=X, padx=(canvas.winfo_width(), 0), anchor="w"
        )
        expration_ayarlar = expration_settings_text.get("1.0", tk.END)
        expration_ayarlar = expration_ayarlar.rstrip("\n")
        write_settings("Settings/expration_settings.txt", expration_ayarlar)
        item_ids = item_ids_text.get(1.0, tk.END).strip("\n")
        username = expration_username_entry.get().strip("\n")
        password = expration_password_entry.get().strip("\n")
        print([username, password])

        if path == "Example: C:/Users/Username/Desktop/sonuc":
            text_print(
                output_text,
                "Maalesef path degeri algilanamadi! Dogru bir deger girdiginizden emin olup tekrar deneyiniz.",
            )
        elif item_ids == "":
            text_print(output_text, "Lütfen düzgün bir shipment id değeri giriniz.")
        else:

            def update_progress(msg: str, color="white"):
                window.after(0, lambda: text_print(output_text, msg, color=color))

            def run_in_thread():
                try:
                    result = process_expiration(
                        username=username,
                        password=password,
                        item_ids_str=item_ids,
                        output_path=path,
                        progress_callback=update_progress,
                    )
                    window.after(
                        0,
                        lambda: text_print(
                            output_text, result["message"], color="#90EE90"
                        ),
                    )
                    window.after(
                        0, lambda p=result["output_path"]: open_folder_in_explorer(p)
                    )
                except Exception as e:
                    window.after(
                        0,
                        lambda: text_print(output_text, f"Hata: {str(e)}", color="red"),
                    )

            Thread(target=run_in_thread, daemon=True).start()
        window.bind("<Configure>", lambda e: expration_resize(e, 1))

    def expration_resize(e, isactive):
        scale = main_frame_resize()
        height = (
            expration_bottom_canvas.winfo_y()
            + expration_bottom_canvas.winfo_height()
            + 20
            + isactive * output_text.winfo_height()
        )
        if height < canvas2.winfo_height():
            block_frame.config(width=750 * scale, height=canvas2.winfo_height())
        else:
            block_frame.config(width=750 * scale, height=height)
        expration_login_main_frame.grid_columnconfigure(
            0, weight=1, minsize=300 * scale
        )
        if scale >= 1.3:
            expration_settings_text.config(
                font=("JetBrainsMonoRoman Regular", round(10 * (scale - 0.3)))
            )
            if scale >= 1.4:
                expration_username_entry.config(
                    font=("JetBrainsMonoRoman Regular", round(12 * (scale - 0.4)))
                )
                expration_password_entry.config(
                    font=("JetBrainsMonoRoman Regular", round(12 * (scale - 0.4)))
                )
        if isactive == 1:
            output_text.pack_configure(padx=(canvas.winfo_width(), 0))
        canvas2.config(scrollregion=canvas2.bbox("all"))

    block_frame = Frame(
        canvas2, background=color, width=750, height=canvas2.winfo_height()
    )
    canvas2.create_window((0, 0), window=block_frame, anchor="nw")
    canvas2.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas2))
    expration_scrollbar = MyScrollbar(
        window,
        target=canvas2,
        command=canvas2.yview,
        thumb_thickness=8,
        thumb_color="#888888",
        thickness=18,
        line_color=line_color,
    )
    canvas2.config(
        yscrollcommand=expration_scrollbar.set, scrollregion=canvas2.bbox("all")
    )
    expration_scrollbar.pack(side=RIGHT, fill=tk.Y)
    expration_top_canvas = Canvas(
        block_frame, background=color, border=0, highlightthickness=0
    )
    expration_bottom_canvas = Canvas(
        block_frame, background=color, border=0, highlightthickness=0
    )
    expration_title = Label(
        expration_top_canvas,
        background=color,
        foreground=canvas2_text_color,
        text="Expration Date",
        font=("JetBrainsMonoRoman Regular", 24 * -1),
    )
    expration_title_line = Frame(expration_top_canvas, background=line_color, height=2)
    save_path_label = Label(
        expration_top_canvas,
        background=color,
        fg=canvas2_text_color,
        text="Sonuçların kaydedilmesini istediğiniz klasörün yolunu giriniz:",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    path_frame = Frame(expration_top_canvas, background=color, height=30)
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
        placeholder_saver("exp", save_path)

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

    expration_login_main_frame = Frame(
        expration_bottom_canvas,
        background=color,
    )
    expration_username_label = Label(
        expration_login_main_frame,
        text="Kullanici Adi:",
        background=color,
        foreground=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12),
    )
    expration_username_entry = tk.Entry(
        expration_login_main_frame,
        border=0,
        highlightthickness=3,
        highlightcolor=line_color,
        highlightbackground=line_color,
        background=line_color,
        insertbackground=canvas2_text_color,
        foreground=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12),
    )
    expration_password_label = Label(
        expration_login_main_frame,
        text="Şifre:",
        background=color,
        foreground=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12),
    )
    expration_password_entry = tk.Entry(
        expration_login_main_frame,
        border=0,
        highlightthickness=3,
        highlightcolor=line_color,
        highlightbackground=line_color,
        background=line_color,
        insertbackground=canvas2_text_color,
        foreground=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12),
    )
    button_group = Frame(
        expration_login_main_frame,
        background=color,
        width=300,
    )
    baslat_button = MyButton(
        button_group,
        round=12,
        width=100,
        height=40,
        text="Başlat",
        background=line_color,
        text_color="white",
        align_text="center",
    )

    baslat_button.bind(
        "<Button-1>", lambda e: baslat_click(e, "#8AB4F8", "black", baslat_button)
    )
    baslat_button.bind(
        "<ButtonRelease-1>",
        lambda e: color_change(e, "#727478", "white", baslat_button),
    )
    baslat_button.bind(
        "<Enter>",
        lambda e: color_change(e, "#727478", canvas2_text_color, baslat_button),
    )
    baslat_button.bind(
        "<Leave>", lambda e: color_change(e, line_color, "white", baslat_button)
    )

    baslat_button.pack(side=RIGHT, padx=(10, 0))
    settings_height = 150
    if "expration_settings.txt" not in os.listdir("Settings"):
        write_settings("Settings/expration_settings.txt", expration_settings_var)
    expration_settings_text = Text(
        expration_bottom_canvas,
        border=0,
        wrap=WORD,
        bg=line_color,
        fg="#c0c0c0",
        height=int(settings_height / 15),
        font=("JetBrainsMonoRoman Regular", 10),
        insertbackground="#c0c0c0",
    )

    login_dictionary = {"default_email": [], "default_password": []}
    with open("Settings/expration_settings.txt", "r", encoding="utf-8") as file:
        readed = file.read()
        expration_settings_text.insert(tk.END, readed)
        expration_settings_text.see(tk.END)
        lines = readed.split("\n")
        for line in lines:
            line = line.split("=")
            if line[0] == "default_email" or line[0] == "default_email ":
                degerler = line[1].split(",")
                for deger in degerler:
                    deger = deger.replace("\n", "")
                    deger = deger.replace(" ", "", 1)
                    login_dictionary["default_email"].append(deger)
            elif line[0] == "default_password" or line[0] == "default_password ":
                degerler = line[1].split(",")
                for deger in degerler:
                    deger = deger.replace("\n", "")
                    deger = deger.replace(" ", "", 1)
                    login_dictionary["default_password"].append(deger)
        if expration_password_entry.get() == "":
            expration_password_entry.insert(0, login_dictionary["default_password"][0])
        if expration_username_entry.get() == "":
            expration_username_entry.insert(0, login_dictionary["default_email"][0])
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

    item_ids_label = Label(
        expration_top_canvas,
        text="Aşağıya shipment id'lerini giriniz.(birden fazla id girilecek ise virgül ile ayırınız.):",
        background=color,
        font=("JetBrainsMonoRoman Regular", 12),
        fg=canvas2_text_color,
    )
    item_ids_text = Text(
        expration_top_canvas,
        height=1,
        border=0,
        fg=canvas2_text_color,
        bg=line_color,
        font=("JetBrainsMonoRoman Regular", 12),
        pady=4,
        insertbackground="#c0c0c0",
    )

    block_frame.grid_propagate(False)
    block_frame.grid_columnconfigure(0, weight=1)
    expration_top_canvas.grid_columnconfigure(0, weight=1)
    expration_bottom_canvas.grid_columnconfigure(0, weight=1)
    expration_top_canvas.grid(column=0, row=0, sticky="ew", padx=(25, 0), pady=(25, 0))
    expration_bottom_canvas.grid(column=0, row=1, sticky="ew", padx=(25, 0))
    expration_title.grid(column=0, row=0, sticky="w")
    expration_title_line.grid(column=0, row=1, sticky="we")

    expration_login_main_frame.grid_columnconfigure(0, weight=1, minsize=300)
    expration_login_main_frame.grid(column=0, row=0, sticky="w")
    expration_settings_text.grid(column=0, row=1, sticky="we", pady=(25, 0))
    expration_username_label.grid(column=0, row=0, sticky="w", pady=(25, 5))
    expration_username_entry.grid(column=0, row=1, sticky="we")
    expration_password_label.grid(column=0, row=2, sticky="w", pady=(10, 5))
    expration_password_entry.grid(column=0, row=3, sticky="we")
    button_group.grid(column=0, row=4, sticky="ew", pady=(15, 0))

    save_path_label.grid(column=0, row=3, sticky="w", pady=(15, 0))
    path_frame.grid(column=0, row=4, sticky="we")
    item_ids_label.grid(column=0, row=7, sticky="w", pady=(15, 0))
    item_ids_text.grid(column=0, row=8, sticky="we")
    browse_button.pack(side=tk.RIGHT, padx=(8, 0))
    save_button.pack(side=tk.RIGHT, padx=(8, 0))
    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function("exp", save_path, placeholder)
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

    canvas2.config(scrollregion=canvas2.bbox("all"))
    window.bind("<Configure>", lambda e: expration_resize(e, 0))
