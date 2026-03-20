import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, X, RIGHT, LEFT, BOTH, END
import os

from utils.file_operations import (
    browse_directory,
    placeholder_saver,
    path_text_function,
    browse_excel,
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
from gui.components.custom_buttons import SwitchButton
from core.invoice_finder import process_invoice_finder, process_invoice_finder_upc


import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread


def render_invoicefinder_view(
    canvas,
    canvas2,
    main_frame_resize,
    window,
    color,
    line_color,
    canvas2_text_color,
    dosyalar_dictionary,
):
    def invoicefinder_resize(e, a):
        scale = main_frame_resize()
        invoice_finder_drop_frame.config(height=175 * scale)
        height = bottom_frame.winfo_y() + bottom_frame.winfo_height() + 20
        if a:
            output_text.pack_configure(padx=(canvas.winfo_width(), 0))
            if height < canvas2.winfo_height() - 200:
                inner_frame.config(width=750 * scale, height=canvas2.winfo_height())
            else:
                inner_frame.config(width=750 * scale, height=height + 200)
        else:
            if height < canvas2.winfo_height():
                inner_frame.config(width=750 * scale, height=canvas2.winfo_height())
            else:
                inner_frame.config(width=750 * scale, height=height)
        canvas2.config(scrollregion=canvas2.bbox("all"))

    inner_frame = Canvas(
        canvas2,
        width=750,
        background=color,
        border=0,
        height=canvas2.winfo_height(),
        highlightthickness=0,
    )
    canvas2.create_window((0, 0), window=inner_frame, anchor="nw")
    invoicefinder_scrollbar = MyScrollbar(
        window,
        target=canvas2,
        command=canvas2.yview,
        thumb_thickness=8,
        thumb_color="#888888",
        thickness=18,
        line_color=line_color,
    )
    canvas2.config(yscrollcommand=invoicefinder_scrollbar.set)
    invoicefinder_scrollbar.pack(side=RIGHT, fill=tk.Y)
    top_frame = Frame(
        inner_frame,
        background=color,
    )
    bottom_frame = Frame(inner_frame, background=color)
    title_frame = Frame(top_frame, background=color)
    title = Label(
        title_frame,
        background=color,
        fg=canvas2_text_color,
        text="Invoice Finder",
        font=("JetBrainsMonoRoman Regular", 24 * -1),
    )
    upc_switch = SwitchButton(
        parent=title_frame,
        border=0,
        highlightthickness=0,
        active_function=lambda: upc_active(),
        pasif_function=lambda: upc_deactive(),
        f="red",
        s="green",
        status=True,
    )
    title.pack(side="left")
    upc_switch.pack(side="right")
    title_line = Frame(top_frame, height=2, bg=line_color)
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
    invoice_path_label = Label(
        top_frame,
        background=color,
        fg=canvas2_text_color,
        text="Invoice Pdf'lerinin bulunduğu klasörün yolunu giriniz:",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    invoice_path_frame = Frame(top_frame, background=color, height=30)
    invoice_save_path = Text(
        invoice_path_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg="#747474",
        background=line_color,
        border=0,
        pady=4,
        insertbackground="#c0c0c0",
    )
    invoice_browse_button = MyButton(
        invoice_path_frame,
        text="Browse",
        background=line_color,
        text_color="white",
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9),
    )
    invoice_save_button = MyButton(
        invoice_path_frame,
        text="Kaydet",
        background=line_color,
        text_color="white",
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9),
    )
    allinvoices_path_label = Label(
        top_frame,
        background=color,
        fg=canvas2_text_color,
        text="Butun invoiceleri iceren excel dosyasinin yolunu giriniz:",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    allinvoices_path_frame = Frame(top_frame, background=color, height=30)
    allinvoices_save_path = Text(
        allinvoices_path_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg="#747474",
        background=line_color,
        border=0,
        pady=4,
        insertbackground="#c0c0c0",
    )
    allinvoices_browse_button = MyButton(
        allinvoices_path_frame,
        text="Browse",
        background=line_color,
        text_color="white",
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9),
    )
    allinvoices_save_button = MyButton(
        allinvoices_path_frame,
        text="Kaydet",
        background=line_color,
        text_color="white",
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9),
    )
    invoice_date_label = Label(
        top_frame,
        background=color,
        fg=canvas2_text_color,
        text="Bir tarih degeri giriniz:",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    invoice_date_text = Text(
        top_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg="#747474",
        background=line_color,
        border=0,
        pady=4,
        insertbackground="#c0c0c0",
    )
    invoice_upc_text = Text(
        top_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg="#747474",
        background=line_color,
        border=0,
        pady=4,
        insertbackground="#c0c0c0",
    )
    invoice_month_label = Label(
        top_frame,
        background=color,
        fg=canvas2_text_color,
        text="Kaç ay öncesinin invoiceları çekilsin giriniz (hepsi için 0 yazınız):",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    invoice_month_text = Text(
        top_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg="#747474",
        background=line_color,
        border=0,
        pady=4,
        insertbackground="#c0c0c0",
    )
    buttons_frame = Frame(
        bottom_frame,
        bg=color,
    )
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
    yonerge_button = MyButton(
        buttons_frame,
        round=12,
        width=100,
        height=40,
        text="Yönerge",
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

    def upc_deactive():
        invoice_date_text.grid_forget()
        invoice_upc_text.grid(column=0, row=9, sticky="we")
        invoice_month_label.grid(column=0, row=10, sticky="w")
        invoice_month_text.grid(column=0, row=11, sticky="we")
        invoice_date_text.config(state=tk.NORMAL)
        invoice_upc_text.config(state=tk.NORMAL)
        invoice_date_label.config(text="Upc değer(ler)ini giriniz:")
        invoice_finder_drop_frame.grid_forget()
        invoice_finder_surukle_text.grid_forget()

    def upc_active():
        invoice_upc_text.grid_forget()
        invoice_month_label.grid_forget()
        invoice_month_text.grid_forget()
        invoice_date_text.grid(column=0, row=9, sticky="we")
        invoice_date_text.config(state=tk.NORMAL)
        invoice_upc_text.config(state=tk.NORMAL)
        invoice_date_label.config(text="Bir tarih degeri giriniz:")
        invoice_finder_surukle_text.grid(column=0, row=0, sticky="w", pady=10)
        invoice_finder_drop_frame.grid(column=0, row=1, sticky="we")

    def browse_click(event, c, t, text_item, b):
        browse_color_change(event, c, t, b)
        browse_directory(text_item, w=window)

    def browse_click_excel(event, c, t, text_item, b):
        browse_color_change(event, c, t, b)
        browse_excel(text_item, w=window)

    def browse_color_change(e, c, t, b):
        b.config(background=c, text_color=t)

    def save_click(event, c, t, b, name, save_path):
        browse_color_change(event, c, t, b)
        placeholder_saver(name, save_path)

    def baslat_click(event, c, t, b):
        b.config(background=c, text_color=t)
        path = save_path.get(1.0, END).strip("\n")
        invoice_folder = invoice_save_path.get(1.0, END).strip("\n")
        date = invoice_date_text.get(1.0, END).strip("\n")
        upc = invoice_upc_text.get(1.0, END).strip("\n")
        allinvoices = allinvoices_save_path.get(1.0, END).strip("\n")
        month = invoice_month_text.get(1.0, END).strip("\n")
        output(path, invoice_folder, date, upc, month, allinvoices)

    def yonerge_click(event, c, t, b):
        b.config(background=c, text_color=t)
        yonerge_window = tk.Tk()
        yonerge_window.geometry("600x400")
        try:
            yonerge_window.iconbitmap("assets/icon.ico")
        except:
            pass
        yonerge_window.title("Invoice Finder Programı Yönergeleri!")
        content_canvas = Canvas(
            yonerge_window, highlightthickness=0, border=0, bg=color
        )
        content_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        main_text = Text(
            content_canvas,
            bg=color,
            fg=canvas2_text_color,
            font=("JetBrainsMonoRoman Regular", 12),
            wrap="word",
            border=0,
        )
        main_text.pack(side=LEFT, fill=BOTH, expand=True, padx=25, pady=25)
        with open("Settings/invoicefinder_yonergeler.txt", encoding="UTF-8") as file:
            z = file.read()
            main_text.insert(tk.END, z)
            main_text.config(state=tk.DISABLED)

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

    invoice_browse_button.bind(
        "<Button-1>",
        lambda e: browse_click(
            e, "#8AB4F8", "black", invoice_save_path, invoice_browse_button
        ),
    )
    invoice_browse_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", invoice_browse_button),
    )
    invoice_browse_button.bind(
        "<Enter>",
        lambda e: browse_color_change(
            e, "#727478", canvas2_text_color, invoice_browse_button
        ),
    )
    invoice_browse_button.bind(
        "<Leave>",
        lambda e: browse_color_change(e, line_color, "white", invoice_browse_button),
    )

    allinvoices_browse_button.bind(
        "<Button-1>",
        lambda e: browse_click_excel(
            e, "#8AB4F8", "black", allinvoices_save_path, allinvoices_browse_button
        ),
    )
    allinvoices_browse_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", allinvoices_browse_button),
    )
    allinvoices_browse_button.bind(
        "<Enter>",
        lambda e: browse_color_change(
            e, "#727478", canvas2_text_color, allinvoices_browse_button
        ),
    )
    allinvoices_browse_button.bind(
        "<Leave>",
        lambda e: browse_color_change(
            e, line_color, "white", allinvoices_browse_button
        ),
    )

    save_button.bind(
        "<Button-1>",
        lambda e: save_click(e, "#8AB4F8", "black", save_button, "fin", save_path),
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

    invoice_save_button.bind(
        "<Button-1>",
        lambda e: save_click(
            e,
            "#8AB4F8",
            "black",
            invoice_save_button,
            "invoice_folder",
            invoice_save_path,
        ),
    )
    invoice_save_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", invoice_save_button),
    )
    invoice_save_button.bind(
        "<Enter>",
        lambda e: browse_color_change(
            e, "#727478", canvas2_text_color, invoice_save_button
        ),
    )
    invoice_save_button.bind(
        "<Leave>",
        lambda e: browse_color_change(e, line_color, "white", invoice_save_button),
    )

    allinvoices_save_button.bind(
        "<Button-1>",
        lambda e: save_click(
            e,
            "#8AB4F8",
            "black",
            allinvoices_save_button,
            "all_invoices",
            allinvoices_save_path,
        ),
    )
    allinvoices_save_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", allinvoices_save_button),
    )
    allinvoices_save_button.bind(
        "<Enter>",
        lambda e: browse_color_change(
            e, "#727478", canvas2_text_color, allinvoices_save_button
        ),
    )
    allinvoices_save_button.bind(
        "<Leave>",
        lambda e: browse_color_change(e, line_color, "white", allinvoices_save_button),
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

    yonerge_button.bind(
        "<Button-1>", lambda e: yonerge_click(e, "#8AB4F8", "black", yonerge_button)
    )
    yonerge_button.bind(
        "<ButtonRelease-1>",
        lambda e: browse_color_change(e, "#727478", "white", yonerge_button),
    )
    yonerge_button.bind(
        "<Enter>",
        lambda e: browse_color_change(e, "#727478", canvas2_text_color, yonerge_button),
    )
    yonerge_button.bind(
        "<Leave>", lambda e: browse_color_change(e, line_color, "white", yonerge_button)
    )

    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    date_placeholder = "GG.AA.YYYY"
    upc_placeholder = "Example: 000000000000, 111111111111"
    month_placeholder = "Example: 14"
    path_text_function("fin", save_path, placeholder)
    path_text_function("invoice_folder", invoice_save_path, placeholder)
    path_text_function("all_invoices", allinvoices_save_path, placeholder)
    window.unbind("<Button-1>")
    save_path.bind(
        "<Button-1>",
        lambda e: on_focus_in(e, save_path, placeholder, canvas2_text_color),
    )
    save_path.bind(
        "<FocusOut>",
        lambda e: on_focus_out(e, save_path, placeholder, canvas2_text_color),
    )
    invoice_save_path.bind(
        "<Button-1>",
        lambda e: on_focus_in(e, invoice_save_path, placeholder, canvas2_text_color),
    )
    invoice_save_path.bind(
        "<FocusOut>",
        lambda e: on_focus_out(e, invoice_save_path, placeholder, canvas2_text_color),
    )
    allinvoices_save_path.bind(
        "<Button-1>",
        lambda e: on_focus_in(
            e, allinvoices_save_path, placeholder, canvas2_text_color
        ),
    )
    allinvoices_save_path.bind(
        "<FocusOut>",
        lambda e: on_focus_out(
            e, allinvoices_save_path, placeholder, canvas2_text_color
        ),
    )
    invoice_date_text.bind(
        "<Button-1>",
        lambda e: on_focus_in(
            e, invoice_date_text, date_placeholder, canvas2_text_color
        ),
    )
    invoice_date_text.bind(
        "<FocusOut>",
        lambda e: on_focus_out(
            e, invoice_date_text, date_placeholder, canvas2_text_color
        ),
    )
    invoice_upc_text.bind(
        "<Button-1>",
        lambda e: on_focus_in(e, invoice_upc_text, upc_placeholder, canvas2_text_color),
    )
    invoice_upc_text.bind(
        "<FocusOut>",
        lambda e: on_focus_out(
            e, invoice_upc_text, upc_placeholder, canvas2_text_color
        ),
    )
    invoice_month_text.bind(
        "<Button-1>",
        lambda e: on_focus_in(
            e, invoice_month_text, month_placeholder, canvas2_text_color
        ),
    )
    invoice_month_text.bind(
        "<FocusOut>",
        lambda e: on_focus_out(
            e, invoice_month_text, month_placeholder, canvas2_text_color
        ),
    )
    invoice_month_text.insert(END, "14")
    invoice_month_text.config(fg=canvas2_text_color)
    invoice_date_text.insert(END, date_placeholder)
    all_placeholders = [
        [save_path, placeholder],
        [invoice_save_path, placeholder],
        [allinvoices_save_path, placeholder],
        [invoice_date_text, date_placeholder],
        [invoice_upc_text, upc_placeholder],
        [invoice_month_text, month_placeholder],
    ]
    window.bind(
        "<Button-1>",
        lambda e: on_click_outside(
            e, all_placeholders, placeholder, canvas2_text_color
        ),
    )

    browse_button.pack(side=RIGHT, padx=(8, 0))
    save_button.pack(side=RIGHT, padx=(8, 0))
    save_path.pack(side=LEFT, fill=X, expand=True)

    invoice_browse_button.pack(side=RIGHT, padx=(8, 0))
    invoice_save_button.pack(side=RIGHT, padx=(8, 0))
    invoice_save_path.pack(side=LEFT, fill=X, expand=True)

    allinvoices_browse_button.pack(side=RIGHT, padx=(8, 0))
    allinvoices_save_button.pack(side=RIGHT, padx=(8, 0))
    allinvoices_save_path.pack(side=LEFT, fill=X, expand=True)

    inner_frame.grid_columnconfigure(0, weight=1)
    inner_frame.grid_propagate(False)
    top_frame.grid(column=0, row=0, sticky="we", padx=(25, 0), pady=(20, 0))
    bottom_frame.grid(column=0, row=1, sticky="we", padx=(25, 0))
    top_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(0, weight=1)
    title_frame.grid(column=0, row=0, sticky="we")
    title_line.grid(column=0, row=1, sticky="we")
    save_path_label.grid(column=0, row=2, sticky="w", pady=(20, 0))
    path_frame.grid(column=0, row=3, sticky="we")
    invoice_path_label.grid(column=0, row=4, sticky="w", pady=(20, 0))
    invoice_path_frame.grid(column=0, row=5, sticky="we")
    allinvoices_path_label.grid(column=0, row=6, sticky="w", pady=(20, 0))
    allinvoices_path_frame.grid(column=0, row=7, sticky="we")
    invoice_date_label.grid(column=0, row=8, sticky="w", pady=(20, 0))
    invoice_date_text.grid(column=0, row=9, sticky="we")
    return_list = drag_drop(
        row1=0,
        row=1,
        column=0,
        dict_name="invoice_finder",
        text="Aşağıya siteden aldığınız verileri içeren excel dosyasını sürükleyip bırakınız:",
        parent=bottom_frame,
        padx=0,
        window=window,
        canvas2=canvas2,
        color=color,
        text_color=canvas2_text_color,
        dosyalar_dictionary=dosyalar_dictionary,
    )
    invoice_finder_drop_frame = return_list[0]
    invoice_finder_surukle_text = return_list[1]
    buttons_frame.grid(column=0, row=2, sticky="e", pady=(20, 0))
    baslat_button.pack(side="right", padx=(10, 0))
    yonerge_button.pack(side="right", padx=(10, 0))
    canvas2.config(scrollregion=canvas2.bbox("all"))

    def output(path, invoice_folder, date, upc, month, allinvoices):
        output_text.pack(
            side=tk.BOTTOM, fill=tk.X, padx=(canvas.winfo_width(), 0), anchor="w"
        )

        if path == placeholder or path == "":
            text_print(
                output_text,
                "Hata: Dosyaların kaydedileceği dosya yolu algılanamadı.",
                color="red",
            )
            return
        if invoice_folder == placeholder or invoice_folder == "":
            text_print(
                output_text,
                "Hata: Invoice PDF'lerinin olduğu klasör yolu algılanamadı.",
                color="red",
            )
            return
        if allinvoices == "" or allinvoices == placeholder:
            text_print(
                output_text,
                "Hata: ALL INVOICE excel dosyasının olduğu dosya yolu algılanamadı.",
                color="red",
            )
            return

        source_excel_list = dosyalar_dictionary.get("invoice_finder", [])
        is_date_mode = upc_switch.status

        if is_date_mode and not source_excel_list:
            text_print(
                output_text,
                "Hata: İşlenecek kaynak excel dosyasını sürüklemediniz.",
                color="red",
            )
            return

        def update_progress(msg: str):
            output_text.after(0, lambda: text_print(output_text, msg))

        def run_in_thread():
            try:
                if is_date_mode:
                    if date == "" or date == date_placeholder:
                        raise ValueError(
                            "Lütfen geçerli bir tarih değeri giriniz (GG.AA.YYYY)."
                        )
                    result = process_invoice_finder(
                        source_excel=source_excel_list[0],
                        all_invoices_excel=allinvoices,
                        invoice_pdf_folder=invoice_folder,
                        output_folder=path,
                        user_input_date=date,
                        progress_callback=update_progress,
                    )
                else:
                    if upc == "" or upc == upc_placeholder:
                        raise ValueError("Lütfen geçerli bir UPC değeri giriniz.")
                    if month == "" or month == month_placeholder:
                        raise ValueError("Lütfen geçerli bir Ay değeri giriniz.")
                    result = process_invoice_finder_upc(
                        all_invoices_excel=allinvoices,
                        invoice_pdf_folder=invoice_folder,
                        output_folder=path,
                        upcs_str=upc,
                        months_str=month,
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

        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: invoicefinder_resize(e, 1))

    window.bind("<Configure>", lambda e: invoicefinder_resize(e, 0))
    canvas2.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas2))
