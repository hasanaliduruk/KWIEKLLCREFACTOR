import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

from utils.file_operations import relative_to_assets
from utils.event_handlers import on_mouse_wheel

from tkinter import PhotoImage
import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread


def drag_drop(
    row1,
    row,
    column,
    dict_name,
    text,
    parent,
    window,
    canvas2,
    color,
    text_color,
    dosyalar_dictionary,
    win=0,
    bg_image=0,
    file_image=0,
    file_type=".xlsx",
    padx=25,
    pady=25,
):
    if win == 0:
        win = window
    dosyalar_dictionary[dict_name] = []
    button_list = []
    image_dictionary = {
        "sil_button_image": PhotoImage(
            file=relative_to_assets("image_3.png"), width=35, height=25
        ),
        "excel_dosya_image": PhotoImage(file=relative_to_assets("image_5.png")),
        "drag_drop_image": "",
    }
    if file_image == 0:
        file_image = image_dictionary["excel_dosya_image"]
    surukle_text = Label(
        parent,
        text=text,
        background=color,
        fg=text_color,
        font=("JetBrainsMonoRoman Regular", 12),
    )
    surukle_text.grid(
        column=column, row=row1, columnspan=2, padx=padx, pady=10, sticky="w"
    )

    def on_frame_enter(event):
        canvas2.unbind_all("<MouseWheel>")
        drop_canvas.bind_all("<MouseWheel>", on_mouse_wheel_frame)

    def on_frame_leave(event):
        canvas2.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas2))

    def drag():
        main_canvas.yview_scroll(10, "units")

    def on_mouse_wheel_frame(event):
        drop_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def drop(event):
        main_frame.bind("<Enter>", on_frame_enter)
        main_frame.bind("<Leave>", on_frame_leave)
        drop_canvas.bind_all("<MouseWheel>", on_mouse_wheel_frame)
        drop_canvas.config(scrollregion=drop_canvas.bbox("all"))
        k = 1
        if type(event) == tuple or event == "":
            file_path = list(event)
        else:
            file_path = event.data
            if file_type not in file_path:
                k = 0
                inner_frame.config(
                    height=main_canvas.winfo_height(),
                    width=main_canvas.winfo_width(),
                    bg="#616161",
                )
                inner_frame.pack_propagate(False)
                label = Label(
                    inner_frame,
                    bg="#616161",
                    text="Yanlış dosya tipi algılandı!",
                    fg="white",
                )
                label.pack(side=LEFT, fill=BOTH, expand=True)

                def destroy():
                    label.destroy()
                    inner_frame.config(height=0, bg="#D9D9D9")
                    inner_frame.pack_propagate(True)

                win.after(1000, destroy)
        z = 0
        if type(event) == tuple or event == "":
            file_path = list(event)
            z = 1
        else:
            file_path = event.data.strip().split(file_type)
            z = 0
        for i in file_path:
            if "{" or "}" in i:
                i = i.replace("{", "")
                i = i.replace("}", "")
            if i != "":
                if i[0] == " ":
                    i = i[1:]
                if z == 0:
                    i = i + file_type
                if i not in dosyalar_dictionary[dict_name] and k == 1:
                    inner_frame.grid_propagate(True)
                    dosyalar_dictionary[dict_name].append(i)
                    buttons_frame = Frame(
                        inner_frame,
                        highlightbackground="black",
                        highlightthickness=1,
                        height=30,
                        padx=0,
                        pady=0,
                        width=drop_canvas.winfo_width(),
                    )
                    excel_image = Label(buttons_frame, image=file_image)
                    excel_image.pack(side=LEFT)
                    button = tk.Button(
                        buttons_frame,
                        text=i,
                        font=("JetBrainsMonoRoman Regular", 15 * -1),
                        height=1,
                        border=0,
                        anchor="w",
                    )
                    inner_frame.columnconfigure(
                        0, weight=1, minsize=drop_canvas.winfo_width()
                    )
                    buttons_frame.grid(
                        column=0,
                        row=dosyalar_dictionary[dict_name].index(i),
                        columnspan=2,
                        padx=0,
                        pady=0,
                        sticky="nswe",
                    )
                    button.pack(side=RIGHT, fill=BOTH, expand=True)
                    parent.update_idletasks()
                    button_width = button.winfo_width()
                    inner_frame.grid_propagate(False)
                    buttons_frame.config(height=30)
                    buttons_frame.pack_propagate(False)

                    button_tik = tk.Button(
                        buttons_frame,
                        image=image_dictionary["sil_button_image"],
                        border=0,
                        width=35,
                        command=lambda b=button, db=None, bl=None: delete_button_func(
                            b, db, bl
                        ),
                    )
                    button_tik.config(
                        command=lambda bf=buttons_frame, b=button, bl=button_list: delete_button_func(
                            bf, b, bl
                        )
                    )

                    def ustunde(event, buttons_frame, button, button_tik):

                        button_tik.place(x=0, y=1)
                        buttons_frame.update()
                        index = dosyalar_dictionary[dict_name].index(
                            button.cget("text")
                        )
                        buttons_frame.update_idletasks()
                        buttons_frame.bind("<Leave>", lambda e: degil(e, button_tik))

                    def degil(event, button_tik):
                        try:
                            button_tik.place_forget()
                        except:
                            pass
                        buttons_frame.update_idletasks()

                    def delete_button_func(buttons_frame, button, button_list):
                        for button1 in button_list:
                            if button1[0] == button:
                                button_list.remove(button1)
                        i = button.cget("text")
                        dosyalar_dictionary[dict_name].remove(i)
                        button.destroy()
                        buttons_frame.destroy()

                        if len(dosyalar_dictionary[dict_name]) == 0:
                            inner_frame.config(height=0)
                        else:
                            update_buttons()
                        # Tuşlar silindiği için frame güncellenmeli

                    def update_buttons():
                        for button in button_list:
                            i = button[0].cget("text")
                            button[2].grid_configure(
                                row=dosyalar_dictionary[dict_name].index(i)
                            )
                            # parent.update_idletasks()
                            button_width = button[0].winfo_width()
                            """
                            if len(dosyalar_dictionary[dict_name]) == 0:
                                inner_frame.config(height=0)
                            elif 20+30*len(dosyalar_dictionary[dict_name]) > drop_canvas.winfo_height():
                                inner_frame.config(height=20+30*len(dosyalar_dictionary[dict_name]))
                            else:
                                inner_frame.config(height=drop_canvas.winfo_height())
                            button[2].config(width= inner_frame.winfo_width())
                            """
                            # parent.update_idletasks()

                    def update_size(button_list, inner_frame):
                        inner_frame.update()
                        for i in button_list:
                            i[2].config(width=inner_frame.winfo_width())
                            parent.update_idletasks()

                    button_list.append([button, "h", buttons_frame])

                    # button_tik.place(x=button_width + 15, y=2+30*(dosyalar_dictionary[dict_name].index(i)))
                    # button_tik.place(x=button_width + 15, y=0)
                    buttons_frame.bind(
                        "<Enter>",
                        lambda e, bf=buttons_frame, b=button, bt=button_tik: ustunde(
                            e, bf, b, bt
                        ),
                    )
                    parent.update_idletasks()
                    inframe_width = drop_canvas.winfo_width()
                    buttons_frame.configure(width=button.winfo_width() + 30)
                    parent.update_idletasks()
                    toplam = buttons_frame.winfo_width()
                    if (
                        10 + (30 * (len(dosyalar_dictionary[dict_name])))
                    ) > drop_canvas.winfo_height():
                        inner_frame.config(
                            height=10 + (30 * (len(dosyalar_dictionary[dict_name])))
                        )
                    else:
                        inner_frame.config(height=drop_canvas.winfo_height() - 5)
                    if toplam > inframe_width:
                        scrollbar_h.grid(column=0, row=1, sticky="ew")
                        inner_frame.config(width=toplam)

                    # update_size(button_list, inner_frame)
                    # parent.update_idletasks()

    main_frame = Frame(
        parent,
        background="#3F4042",
        borderwidth=0,
        relief="solid",
        highlightcolor="#3F4042",
        highlightthickness=6,
        highlightbackground="#3F4042",
    )
    main_frame.grid(column=column, row=row, columnspan=2, sticky="nwes", padx=padx)
    main_canvas = Canvas(main_frame, bg="white")
    main_canvas.pack(side=LEFT, fill=BOTH, expand=True)
    drop_canvas = Canvas(main_canvas, bg="white", height=150)

    if bg_image == 0:
        image_dictionary["drag_drop_image"] = PhotoImage(
            file=relative_to_assets("image_6.png")
        )
        bg_image = image_dictionary["drag_drop_image"]
    else:
        pass
    main_canvas.grid_columnconfigure(0, weight=1)
    main_canvas.grid_rowconfigure(0, weight=1)
    drop_canvas.grid(column=0, row=0, sticky="nsew")
    drop_canvas.pack_propagate(False)
    drag_drop_label = Label(drop_canvas, bg="#D9D9D9")
    drag_drop_label.background_image = bg_image
    drag_drop_label.config(image=bg_image)
    drag_drop_label.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar_v = tk.Scrollbar(
        main_canvas, orient=tk.VERTICAL, command=drop_canvas.yview
    )
    scrollbar_v.grid(column=1, row=0, sticky="ns")
    drop_canvas.config(yscrollcommand=scrollbar_v.set)

    scrollbar_h = tk.Scrollbar(
        main_canvas, orient=tk.HORIZONTAL, command=drop_canvas.xview
    )

    drop_canvas.config(xscrollcommand=scrollbar_h.set)

    inner_frame = Frame(
        drop_canvas, bg="#D9D9D9", height=0, width=main_canvas.winfo_width()
    )
    drop_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def config(e):
        inner_frame.config(width=e.width)

    inner_frame.bind(
        "<Configure>",
        lambda e: drop_canvas.config(scrollregion=drop_canvas.bbox("all")),
    )
    main_canvas.bind("<Configure>", lambda e: config(e))
    a = 0

    # Sürükle bırak işlemi için hedef belirleme
    def drop_canvas_click(event):
        if file_type == ".xlsx":
            file_path = filedialog.askopenfilename(
                parent=win,
                title="Bir Excel dosyası seçin",
                filetypes=[
                    ("Excel Files", "*.xlsx *.xls")
                ],  # Sadece Excel dosyalarını filtreler
                multiple=True,
            )
        else:
            file_path = filedialog.askopenfilename(
                parent=win,
                title="Bir Excel dosyası seçin",
                filetypes=[
                    ("Excel Files", "*{}".format(file_type))
                ],  # Sadece Excel dosyalarını filtreler
                multiple=True,
            )
        drop(file_path)

    drag_drop_label.bind("<Button-1>", drop_canvas_click)
    drop_canvas.drop_target_register(DND_FILES)

    drop_canvas.dnd_bind("<<Drop>>", lambda e: drop(e))
    return [main_frame, surukle_text]


def ham_drag_drop2(
    row1,
    row,
    column,
    dict_name,
    text,
    parent,
    window,
    canvas2,
    dosyalar_dictionary,
    color,
    text_color,
):
    dosyalar_dictionary[dict_name] = []
    button_list = []
    sil_button_image = PhotoImage(
        file=relative_to_assets("image_3.png"), width=35, height=25
    )
    excel_dosya_image = PhotoImage(file=relative_to_assets("image_5.png"))
    surukle_text = Label(
        parent,
        text=text,
        background=color,
        fg=text_color,
    )
    surukle_text.grid(
        column=column, row=row1, columnspan=2, padx=25, pady=10, sticky="w"
    )

    def on_frame_enter(event):
        canvas2.unbind_all("<MouseWheel>")
        drop_canvas.bind_all("<MouseWheel>", on_mouse_wheel_frame)

    def on_frame_leave(event):
        canvas2.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas2))

    def drag():
        main_canvas.yview_scroll(10, "units")

    def on_mouse_wheel_frame(event):
        drop_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def drop(event):
        main_frame.bind("<Enter>", on_frame_enter)
        main_frame.bind("<Leave>", on_frame_leave)
        drop_canvas.bind_all("<MouseWheel>", on_mouse_wheel_frame)
        drop_canvas.config(scrollregion=drop_canvas.bbox("all"))

        k = 1
        if type(event) == tuple or event == "":
            file_path = event
        else:
            file_path = event.data
            if ".xlsx" not in file_path:
                k = 0
                inner_frame.config(
                    height=main_canvas.winfo_height(),
                    width=main_canvas.winfo_width(),
                    bg="#616161",
                )
                inner_frame.pack_propagate(False)
                label = Label(
                    inner_frame,
                    bg="#616161",
                    text="Yanlış dosya tipi algılandı!",
                    fg="white",
                )
                label.pack(side=LEFT, fill=BOTH, expand=True)

                def destroy():
                    label.destroy()
                    inner_frame.config(height=0, bg="#D9D9D9")
                    inner_frame.pack_propagate(True)

                window.after(1000, destroy)
        z = 0
        if type(event) == tuple or event == "":
            file_path = event
            z = 1
        else:
            file_path = event.data.strip().split(".xlsx")
            z = 0
        for i in file_path:
            if "{" or "}" in i:
                i = i.replace("{", "")
                i = i.replace("}", "")
            if i != "":
                if i[0] == " ":
                    i = i[1:]
                if z == 0:
                    i = i + ".xlsx"
                if i not in dosyalar_dictionary[dict_name] and k == 1:

                    def button_click(event):
                        var.set("1")
                        vary.set(event.y)

                    def button_release(event):
                        var.set("0")
                        to = int(surukle_line.grid_info()["row"] / 2)
                        index = dosyalar_dictionary[dict_name].index(
                            event.widget.cget("text")
                        )
                        print(index)
                        tasi(dosyalar_dictionary[dict_name], index, to)
                        surukle_line.grid_forget()

                    def button_motion(event):
                        if var.get() == "1":
                            y = event.y
                            if y >= 0:
                                which_file = int((y + vary.get()) / 30)
                            else:
                                which_file = int((y - vary.get()) / 30)
                            # print(which_file)
                            which_row = 2 * which_file

                            row = event.widget.master.grid_info()["row"] + which_row - 1
                            if row < 0:
                                row = 0
                            surukle_line.grid(column=0, row=row, sticky="ew")
                            """elif y > 15 and y <=30:
                                row = event.widget.master.grid_info()['row']+which_row + 1
                                print(row)
                                surukle_line.grid(column=0, row=row, sticky='ew')"""

                    inner_frame.grid_propagate(True)
                    dosyalar_dictionary[dict_name].append(i)
                    buttons_frame = Frame(
                        inner_frame,
                        highlightbackground="black",
                        highlightthickness=1,
                        height=30,
                        padx=0,
                        pady=0,
                        width=drop_canvas.winfo_width(),
                    )
                    excel_image = Label(buttons_frame, image=excel_dosya_image)
                    excel_image.pack(side=LEFT)
                    button = Label(
                        buttons_frame,
                        text=i,
                        font=("JetBrainsMonoRoman Regular", 15 * -1),
                        height=1,
                        border=0,
                        anchor="w",
                    )
                    inner_frame.columnconfigure(
                        0, weight=1, minsize=drop_canvas.winfo_width()
                    )
                    buttons_frame.grid(
                        column=0,
                        row=2 * dosyalar_dictionary[dict_name].index(i) + 1,
                        columnspan=2,
                        padx=0,
                        pady=0,
                        sticky="nswe",
                    )
                    button.pack(side=RIGHT, fill=BOTH, expand=True)
                    button.bind("<Button-1>", button_click)
                    button.bind("<ButtonRelease-1>", button_release)
                    button.bind("<B1-Motion>", lambda e: button_motion(e))

                    # button.bind("<<ButtonRelease-1>>", button_release())

                    parent.update_idletasks()
                    button_width = button.winfo_width()
                    inner_frame.grid_propagate(False)
                    buttons_frame.config(height=30)
                    buttons_frame.pack_propagate(False)

                    var = tk.StringVar()
                    var.set("0")
                    vary = tk.IntVar()

                    def tasi(lst, from_index, to_index):
                        if from_index < 0 or from_index >= len(lst):
                            raise IndexError("from_index is out of bounds")
                        if to_index < 0 or to_index >= len(lst):
                            raise IndexError("to_index is out of bounds")

                        # Öğeyi çıkart ve yeni konuma ekle
                        item = lst.pop(from_index)
                        lst.insert(to_index, item)

                        update_buttons()

                    button_tik = tk.Button(
                        buttons_frame,
                        image=sil_button_image,
                        border=0,
                        width=35,
                        command=lambda b=button, db=None, bl=None: delete_button_func(
                            b, db, bl
                        ),
                    )
                    button_tik.config(
                        command=lambda bf=buttons_frame, b=button, bl=button_list: delete_button_func(
                            bf, b, bl
                        )
                    )
                    yukari_button = tk.Button(
                        buttons_frame,
                        text="yukari",
                    )
                    asagi_button = tk.Button(
                        buttons_frame,
                        text="asagi",
                    )

                    def ustunde(
                        event,
                        buttons_frame,
                        button,
                        button_tik,
                        yukari_button,
                        asagi_button,
                    ):

                        button_tik.place(x=0, y=1)
                        buttons_frame.update()
                        index = dosyalar_dictionary[dict_name].index(
                            button.cget("text")
                        )
                        yukari_button.config(
                            command=lambda: tasi(
                                dosyalar_dictionary[dict_name], index, index - 1
                            )
                        )
                        asagi_button.config(
                            command=lambda: tasi(
                                dosyalar_dictionary[dict_name], index, index + 1
                            )
                        )
                        yukari_button.place(x=button_tik.winfo_width() + 5, y=0)

                        asagi_button.place(x=button_tik.winfo_width() + 55, y=0)

                        buttons_frame.update_idletasks()
                        buttons_frame.bind(
                            "<Leave>",
                            lambda e: degil(e, button_tik, asagi_button, yukari_button),
                        )

                    def degil(event, button_tik, asagi_button, yukari_button):
                        try:
                            button_tik.place_forget()
                        except:
                            pass
                        try:
                            yukari_button.place_forget()
                        except:
                            pass
                        try:
                            asagi_button.place_forget()
                        except:
                            pass
                        buttons_frame.update_idletasks()

                    def delete_button_func(buttons_frame, button, button_list):
                        for button1 in button_list:
                            if button1[0] == button:
                                button_list.remove(button1)
                        i = button.cget("text")
                        dosyalar_dictionary[dict_name].remove(i)
                        button.destroy()
                        buttons_frame.destroy()

                        if len(dosyalar_dictionary[dict_name]) == 0:
                            inner_frame.config(height=0)
                        else:
                            update_buttons()
                        # Tuşlar silindiği için frame güncellenmeli

                    def update_buttons():
                        for button in button_list:
                            i = button[0].cget("text")
                            button[2].grid_configure(
                                row=2 * (dosyalar_dictionary[dict_name].index(i)) + 1
                            )
                            # parent.update_idletasks()
                            button_width = button[0].winfo_width()
                            """
                            if len(dosyalar_dictionary[dict_name]) == 0:
                                inner_frame.config(height=0)
                            elif 20+30*len(dosyalar_dictionary[dict_name]) > drop_canvas.winfo_height():
                                inner_frame.config(height=20+30*len(dosyalar_dictionary[dict_name]))
                            else:
                                inner_frame.config(height=drop_canvas.winfo_height())
                            button[2].config(width= inner_frame.winfo_width())
                            """
                            # parent.update_idletasks()

                    def update_size(button_list, inner_frame):
                        inner_frame.update()
                        for i in button_list:
                            i[2].config(width=inner_frame.winfo_width())
                            parent.update_idletasks()

                    button_list.append([button, "h", buttons_frame])

                    # button_tik.place(x=button_width + 15, y=2+30*(dosyalar_dictionary[dict_name].index(i)))
                    # button_tik.place(x=button_width + 15, y=0)
                    buttons_frame.bind(
                        "<Enter>",
                        lambda e, bf=buttons_frame, b=button, bt=button_tik, y=yukari_button, a=asagi_button: ustunde(
                            e, bf, b, bt, y, a
                        ),
                    )
                    parent.update_idletasks()
                    inframe_width = drop_canvas.winfo_width()
                    buttons_frame.configure(width=button.winfo_width() + 30)
                    parent.update_idletasks()
                    toplam = buttons_frame.winfo_width()
                    if (
                        10 + (30 * (len(dosyalar_dictionary[dict_name])))
                    ) > drop_canvas.winfo_height():
                        inner_frame.config(
                            height=10 + (30 * (len(dosyalar_dictionary[dict_name])))
                        )
                    else:
                        inner_frame.config(height=drop_canvas.winfo_height() - 5)
                    if toplam > inframe_width:
                        scrollbar_h.grid(column=0, row=1, sticky="ew")
                        inner_frame.config(width=toplam)

                    # update_size(button_list, inner_frame)
                    # parent.update_idletasks()

    main_frame = Frame(
        parent,
        background="#3F4042",
        border=0,
        relief="solid",
        highlightcolor="#3F4042",
        highlightthickness=6,
        highlightbackground="#3F4042",
    )
    main_frame.grid(column=column, row=row, columnspan=2, sticky="nwes", padx=25)
    main_canvas = Canvas(main_frame, bg="white")
    main_canvas.pack(side=LEFT, fill=BOTH, expand=True)
    drop_canvas = Canvas(main_canvas, bg="white", height=150)
    drag_drop_image = PhotoImage(file=relative_to_assets("image_6.png"))
    main_canvas.grid_columnconfigure(0, weight=1)
    main_canvas.grid_rowconfigure(0, weight=1)
    drop_canvas.grid(column=0, row=0, sticky="nsew")
    drop_canvas.pack_propagate(False)
    drag_drop_label = Label(drop_canvas, bg="#D9D9D9")
    drag_drop_label.background_image = drag_drop_image
    drag_drop_label.config(image=drag_drop_image)
    drag_drop_label.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar_v = tk.Scrollbar(
        main_canvas, orient=tk.VERTICAL, command=drop_canvas.yview
    )
    scrollbar_v.grid(column=1, row=0, sticky="ns")
    drop_canvas.config(yscrollcommand=scrollbar_v.set)

    scrollbar_h = tk.Scrollbar(
        main_canvas, orient=tk.HORIZONTAL, command=drop_canvas.xview
    )

    drop_canvas.config(xscrollcommand=scrollbar_h.set)

    inner_frame = Frame(
        drop_canvas,
        bg="#D9D9D9",
        height=0,
        width=main_canvas.winfo_width(),
        border=0,
        highlightthickness=0,
    )
    surukle_line = Frame(inner_frame, bg="black", height=5)
    drop_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def config(e):
        inner_frame.config(width=e.width)

    inner_frame.bind(
        "<Configure>",
        lambda e: drop_canvas.config(scrollregion=drop_canvas.bbox("all")),
    )
    main_canvas.bind("<Configure>", lambda e: config(e))
    a = 0

    def drop_canvas_click(event):
        file_path = filedialog.askopenfilename(
            parent=window,
            title="Bir Excel dosyası seçin",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls")
            ],  # Sadece Excel dosyalarını filtreler
            multiple=True,
        )
        drop(file_path)

    drag_drop_label.bind("<Button-1>", drop_canvas_click)
    # Sürükle bırak işlemi için hedef belirleme
    drop_canvas.drop_target_register(DND_FILES)

    drop_canvas.dnd_bind("<<Drop>>", lambda e: drop(e))

    return [main_frame, surukle_text]
