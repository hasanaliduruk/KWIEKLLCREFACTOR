import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread
import os

from utils.gui_helpers import text_print, open_folder_in_explorer
from utils.file_operations import browse_directory, placeholder_saver, path_text_function, write_settings, relative_to_assets
from utils.event_handlers import on_focus_in, on_focus_out, on_click_outside, on_mouse_wheel, on_text_enter, on_text_leave
from gui.components.custom_buttons import MyButton
from gui.components.scrollbar import MyScrollbar
from core.tsv_converter import convert_tsv_to_excel
from gui.components.drag_drop import drag_drop

from tkinter import PhotoImage
import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread

tsv_settings_var = (
    "columns = Merchant SKU, Title, ASIN, FNSKU, external-id, Condition, Shipped"
)

def render_tsv_view(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, main_frame_resize):
    def tsv_resize(e, a):
        scale = main_frame_resize()
        tvs_drop_frame.config(height=175*scale)
        height = alt_canvas.winfo_y()+alt_canvas.winfo_height()+20
        if a:
            tsv_output.pack_configure(padx=(canvas.winfo_width(), 0))
            if height < canvas2.winfo_height()-200:
                tvs_main_frame.config(width=750*scale, height=canvas2.winfo_height())
            else:
                tvs_main_frame.config(width=750*scale, height=height+200)
        else:
            if height < canvas2.winfo_height():
                tvs_main_frame.config(width=750*scale, height=canvas2.winfo_height())
            else:
                tvs_main_frame.config(width=750*scale, height=height)
        canvas2.config(scrollregion=canvas2.bbox('all'))
    tvs_main_frame = Frame(
        canvas2,
        bg=color,
        height=canvas2.winfo_height(),
        width=750
    )
    canvas2.create_window((0,0), anchor='nw', window=tvs_main_frame)
    canvas2.config(scrollregion=canvas2.bbox("all"))
    #tvs_main_frame.pack(side=LEFT,fill=BOTH, expand=True)
    canvas2.bind_all('<MouseWheel>', lambda e: on_mouse_wheel(e, canvas2))
    tsv_scrollbar = MyScrollbar(window, target=canvas2, command=canvas2.yview, thumb_thickness=8, thumb_color='#888888', thickness=18, line_color=line_color)
    canvas2.config(yscrollcommand=tsv_scrollbar.set, scrollregion=canvas2.bbox('all'))
    tsv_scrollbar.pack(side=RIGHT, fill=tk.Y)
    tvs_main_frame.grid_columnconfigure(0, weight=1)
    tvs_main_frame.grid_propagate(False)
    ust_canvas = Canvas(
        tvs_main_frame,
        border=0,
        highlightthickness=0,
        bg=color
    )
    ust_canvas.grid(column=0, row=0, sticky='we', padx=(25,0), pady=(25,0))
    ust_canvas.grid_columnconfigure(0, weight=1)
    alt_canvas = Canvas(
        tvs_main_frame,
        border=0,
        highlightthickness=0,
        bg=color,
    )
    alt_canvas.grid(column=0, row=1, sticky='we', padx=(0,0))
    alt_canvas.grid_columnconfigure(0, weight=1)
    title = Label(
        ust_canvas,
        text="TSV PROGRAMI",
        bg=color,
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 24 * -1)
    )
    title.grid(column=0, row=0, sticky="w")
    tsv_title_line = Frame(
        ust_canvas,
        height=2,
        bg=line_color,
        border=0,
        highlightthickness=0
    )
    tsv_title_line.grid(column=0, row=1, sticky="we")
    tsv_path_label = Label(
        ust_canvas,
        text="Aşağıya sonuçların kaydedilmesini istediğiniz dosya yolunu giriniz:",
        background=color,
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12)
    )
    tsv_path_label.grid(column=0, row=2, sticky="w", pady=(25,0))

    tsv_path_frame = Frame(ust_canvas, bg=color, height=30)
    tsv_path_frame.grid(column=0, row=3, sticky="we", pady=(0,25))
    tsv_path_text = Text(
        tsv_path_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg='#747474',
        bg=line_color,
        border=0,
        pady=4,
        insertbackground='#c0c0c0'
    )
    tsv_browse_button = MyButton(
        tsv_path_frame,
        text='Browse',
        background=line_color,
        text_color='white',
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9)
    )
    save_button = MyButton(
        tsv_path_frame,
        text='Kaydet',
        background=line_color,
        text_color='white',
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9)
    )
    def browse_click(event, c, t, text_item, b):
        browse_color_change(event,c,t,b)
        browse_directory(text_item , w=window)
    def browse_color_change(e,c,t,b):
        b.config(background=c, text_color=t)
    def save_click(event, c, t, b):
        browse_color_change(event,c,t,b)
        placeholder_saver('tsv', tsv_path_text)
    tsv_browse_button.bind("<Button-1>", lambda e: browse_click(e,'#8AB4F8','black', tsv_path_text, tsv_browse_button))
    tsv_browse_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', tsv_browse_button))
    tsv_browse_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, tsv_browse_button))
    tsv_browse_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', tsv_browse_button))
    save_button.bind("<Button-1>", lambda e: save_click(e,'#8AB4F8','black', save_button))
    save_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', save_button))
    save_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, save_button))
    save_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', save_button))
    tsv_browse_button.pack(side=RIGHT, padx=(8,0))
    save_button.pack(side=RIGHT, padx=(8,0))
    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function('tsv', tsv_path_text, placeholder)
    window.unbind("<Button-1>")
    tsv_path_text.pack(side=LEFT, fill=X, expand=True)
    tsv_path_text.bind("<Button-1>", lambda e: on_focus_in(e, tsv_path_text, placeholder, canvas2_text_color))
    tsv_path_text.bind("<FocusOut>", lambda e: on_focus_out(e, tsv_path_text, placeholder, canvas2_text_color))
    window.bind("<Button-1>", lambda e: on_click_outside(e, tsv_path_text, placeholder, canvas2_text_color))




    tvs_bg_image = PhotoImage(
        file=relative_to_assets('tvs_bg_rs.png')
    )
    tvs_file_image = PhotoImage(
        file=relative_to_assets('TVS_file.png')
    )

    tvs_drop_return = drag_drop(row1=0,row=1,column=0,dict_name="tsv",
                                text=".tsv uzantili dosyalarinizi asagiya surukleyip birakiniz...", parent=alt_canvas,
                                file_image=tvs_file_image, bg_image=tvs_bg_image, file_type=".tsv", padx=(25,0),
                                window=window, canvas2=canvas2, color=color, text_color=canvas2_text_color, dosyalar_dictionary=dosyalar_dictionary)
    tvs_drop_frame = tvs_drop_return[0]
    tvs_surukle_text = tvs_drop_return[1]
    baslat_button = MyButton(
        alt_canvas,
        round=15,
        width=100,
        height=50,
        text='Başlat',
        background=line_color,
        text_color='white',
        align_text='center'
    )

    settings_height=100
    tsv_settings_label = Label(alt_canvas, text='Settings:', font=("JetBrainsMonoRoman Regular", 12), background=color, fg=canvas2_text_color)
    if 'tsv_settings.txt' not in os.listdir('Settings'):
        write_settings('Settings/tsv_settings.txt', tsv_settings_var)
    tsv_settings_text = Text(
        alt_canvas,
        border=0,
        wrap= WORD,
        bg=line_color,
        fg='#c0c0c0',
        height = int(settings_height/15),
        font=("JetBrainsMonoRoman Regular", 10),
        insertbackground='#c0c0c0'
    )
    tsv_settings_text.bind('<Enter>',lambda e: on_text_enter(e, canvas2))
    tsv_settings_text.bind('<Leave>',lambda e: on_text_leave(e, canvas2))
    with open('Settings/tsv_settings.txt', 'r', encoding='utf-8') as file:
        readed = file.read()
        tsv_settings_text.insert(tk.END, readed)
        tsv_settings_text.see(tk.END)
    tsv_settings_label.grid(column=0, row=2, columnspan=2, sticky = 'w', padx=25, pady=3)
    tsv_settings_text.grid(column=0, row=3, columnspan=2, sticky = 'we', padx=(25,0), pady=5)


    baslat_button.grid(column=0, row=4, sticky='e', padx=(0,0), pady=(15,0))
    def color_change(e,c,t):
        baslat_button.config(background=c, text_color=t)
    def baslat_click(e,c,t):
        color_change(e,c,t)
        path = tsv_path_text.get(1.0, END)
        path = path.rstrip("\n")
        output(path)
    baslat_button.bind("<Button-1>", lambda e: baslat_click(e,'#8AB4F8','black'))
    baslat_button.bind("<ButtonRelease-1>", lambda e: color_change(e,'#727478','white'))
    baslat_button.bind("<Enter>", lambda e: color_change(e,'#727478',canvas2_text_color))
    baslat_button.bind("<Leave>", lambda e: color_change(e,line_color,'white'))
    tsv_output = Text(
        window,
        border=0,
        wrap= WORD,
        bg=line_color,
        fg='#c0c0c0',
        height = 10,
        font=("JetBrainsMonoRoman Regular", 13),
        insertbackground='#c0c0c0'
    )

    def output(path):
        tsv_output.pack(side=tk.BOTTOM, fill=tk.X, padx=(canvas.winfo_width(),0))
        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: tsv_resize(e, True))
        
        tsv_ayarlar = tsv_settings_text.get("1.0", tk.END).rstrip("\n")
        write_settings('Settings/tsv_settings.txt', tsv_ayarlar)
        
        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(tsv_output, "Hata: Dosya yolu algılanamadı, lütfen geçerli bir klasör seçin.", color="red")
            return
            
        tsv_files = dosyalar_dictionary.get("tsv", [])
        if not tsv_files:
            text_print(tsv_output, "Hata: İşlenecek TSV dosyası sürüklemediniz.", color="red")
            return

        def update_progress(msg: str):
            tsv_output.after(0, lambda: text_print(tsv_output, msg))

        def run_in_thread():
            try:
                result = convert_tsv_to_excel(
                    tsv_files=tsv_files,
                    target_path=path,
                    target_name="Converted_TSV",
                    progress_callback=update_progress
                )
                tsv_output.after(0, lambda: text_print(tsv_output, result["message"], color='#90EE90'))
                tsv_output.after(0, lambda: open_folder_in_explorer(path))
            except Exception as e:
                tsv_output.after(0, lambda: text_print(tsv_output, f"Hata: {str(e)}", color='red'))

        conversion_thread = Thread(target=run_in_thread, daemon=True)
        conversion_thread.start()


    canvas2.config(scrollregion=canvas2.bbox('all'))
    window.bind("<Configure>", lambda e: tsv_resize(e, False))
