import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread
import os

from utils.gui_helpers import text_print, open_folder_in_explorer
from utils.file_operations import browse_directory, placeholder_saver, path_text_function, write_settings, relative_to_assets
from utils.event_handlers import on_focus_in, on_focus_out, on_click_outside, on_mouse_wheel, on_text_enter, on_text_leave
from gui.components.custom_buttons import MyButton, SwitchButton
from gui.components.scrollbar import MyScrollbar
from core.cost_updater import process_costupdater, process_costupdater2
from gui.components.drag_drop import drag_drop

from tkinter import PhotoImage
import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread

costupdater_settings_var = (
    'cost = cost\n'
    'sku = sku\n'
    'additional cost = additional_cost\n'
    'business pricing = business_pricing\n'
    'bp strategy = bp_strategy\n'
    'qd strategy = qd_strategy\n'
    '====================================\n'
    'BX: 0.3\n'
    'CANDY: 0.3\n'
    'COS: 0.3\n'
    'CS: 0.3\n'
    'CSC: 0.3\n'
    'DL: 0.3\n'
    'FC: 0.3\n'
    'FD: 0.3\n'
    'FL: 0.75\n'
    'FOUR: 0.3\n'
    'FR: 0.3\n'
    'GEMCO: 0.3\n'
    'IL: 0.75\n'
    'JC: 0.3\n'
    'KH: 0.3\n'
    'LR: 0.3\n'
    'MD: 0.75\n'
    'MONIN PUMP SL: 0.3\n'
    'NC: 0.3\n'
    'NF: 0.3\n'
    'NJ: 0.3\n'
    'NK: 0.3\n'
    'NT: 0.3\n'
    'SN: 0.3\n'
    'UC: 0.3\n'
    'UD: 0.3\n'
    'UN: 0.3\n'
    'UPC: 0.3\n'
    'WB: 0.3\n'
    'WEBS: 0.3\n'
)

costupdater2_settings_var = (
    'cost = cost\n'
    'sku = sku\n'
    'additional cost = additional_cost\n'
    'business pricing = business_pricing\n'
    'bp strategy = bp_strategy\n'
    'qd strategy = qd_strategy\n'
    'pkg volume = pkg_volume\n'
    'pkg weight = pkg_weight\n'
    '====================================\n'
    'DC_NAME: ADDITIONAL_COST EQUATION_NUMBER DEPOSIT_COST\n'
    'BX: 0 2 0.70\n'
    'CANDY: 0 2 0.70\n'
    'COS: 0 2 0.70\n'
    'CS: 0 2 0.70\n'
    'CSC: 0 2 0.70\n'
    'DL: 0 2 0.70\n'
    'FC: 0 2 0.70\n'
    'FD: 0 2 0.70\n'
    'FL: 0 1 0.70\n'
    'FOUR: 0 2 0.70\n'
    'FR: 0 2 0.70\n'
    'GEMCO: 0 2 0.70\n'
    'IL: 0 1 0.70\n'
    'JC: 0 2 0.70\n'
    'KH: 0 2 0.70\n'
    'LR: 0 2 0.70\n'
    'MD: 0 1 0.70\n'
    'MONIN PUMP SL: 0 2 0.70\n'
    'NC: 0 2 0.70\n'
    'NF: 0 2 0.70\n'
    'NJ: 0 2 0.70\n'
    'NK: 0 2 0.70\n'
    'NT: 0 2 0.70\n'
    'SN: 0 2 0.70\n'
    'UC: 0 2 0.70\n'
    'UD: 0 2 0.70\n'
    'UN: 0 2 0.70\n'
    'UPC: 0 2 0.70\n'
    'WB: 0 2 0.70\n'
    'WEBS: 0 2 0.70\n'
    'TD: 0 2 0.70\n'
    'IN: 0 1 0.70\n'
    'BL: 0 2 0.70\n'
    'YT: 0 1 0.70\n'
    'BZ: 0 1 0.70\n'
    'MI: 0 2 0.70'
)

def render_costupdater_view(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, main_frame_resize):
    csv_drag_drop_image = PhotoImage(file=relative_to_assets('csv_drag_drop_rs.png'))
    csv_icon_image = PhotoImage(file=relative_to_assets('csv_icon_rs.png'))
    def resize(e, a):
        scale = main_frame_resize()
        height = bottom_canvas.winfo_y()+bottom_canvas.winfo_height()+20
        drag_frame.config(height=175*scale)
        if a:
            output_text.pack_configure(padx=(canvas.winfo_width(), 0))
            if height < canvas2.winfo_height()-200:
                cost_main_frame.config(width=750*scale, height=canvas2.winfo_height())
            else:
                cost_main_frame.config(width=750*scale, height=height+200)
        else:
            if height < canvas2.winfo_height():
                cost_main_frame.config(width=750*scale, height=canvas2.winfo_height())
            else:
                cost_main_frame.config(width=750*scale, height=height)
        canvas2.config(scrollregion=canvas2.bbox('all'))
    def new_active():
        if 'costupdater2_settings.txt' not in os.listdir('Settings'):
            write_settings('Settings/costupdater2_settings.txt', costupdater2_settings_var)
        with open('Settings/costupdater2_settings.txt', 'r', encoding='utf-8') as file:
            readed = file.read()
            settings_text.delete(1.0, tk.END)
            settings_text.insert(tk.END, readed)
            settings_text.see(tk.END)
        baslat_button.bind("<Button-1>", lambda e: baslat2_click(e,'#8AB4F8','black'))
    def new_deactive():
        if 'costupdater_settings.txt' not in os.listdir('Settings'):
            write_settings('Settings/costupdater_settings.txt', costupdater_settings_var)
        with open('Settings/costupdater_settings.txt', 'r', encoding='utf-8') as file:
            readed = file.read()
            settings_text.delete(1.0, tk.END)
            settings_text.insert(tk.END, readed)
            settings_text.see(tk.END)
        baslat_button.bind("<Button-1>", lambda e: baslat_click(e, '#8AB4F8', 'black'))
    cost_main_frame = Frame(
        canvas2,
        bg=color,
        height=canvas2.winfo_height(),
        width=750
    )
    canvas2.create_window((0,0), window=cost_main_frame, anchor='nw')

    canvas2.bind_all('<MouseWheel>', lambda e: on_mouse_wheel(e, canvas2))
    costupdater_scrollbar = MyScrollbar(window, target=canvas2, command=canvas2.yview, thumb_thickness=8, thumb_color='#888888', thickness=18, line_color=line_color)
    canvas2.config(yscrollcommand=costupdater_scrollbar.set, scrollregion=canvas2.bbox('all'))
    costupdater_scrollbar.pack(side=RIGHT, fill=tk.Y)

    cost_main_frame.grid_columnconfigure(0, weight=1)
    cost_main_frame.grid_propagate(False)


    #creating the top and bottom canvas:

    top_canvas = Canvas(
        cost_main_frame,
        background=color,
        highlightthickness=0,
        border=0
    )
    bottom_canvas = Canvas(
        cost_main_frame,
        background=color,
        highlightthickness=0,
        border=0
    )

    #top and bottom canvaslarin yerlesimi:

    top_canvas.grid(column=0, row=0, sticky='ew', padx=(25,0), pady=(20,0))
    top_canvas.grid_columnconfigure(0, weight=1)
    bottom_canvas.grid(column=0, row=1, sticky='ew', padx=(25,0), pady=0)
    bottom_canvas.grid_columnconfigure(0, weight=1)

    #widgets:
    title_frame = Frame(
        top_canvas,
        background=color
    )
    title = Label(
        title_frame,
        background=color,
        fg=canvas2_text_color,
        text="Cost Updater",
        font=(("JetBrainsMonoRoman Regular", 24 * -1))
    )
    new_switch = SwitchButton(
        parent=title_frame,
        border=0,
        highlightthickness=0,
        active_function=lambda: new_active(),
        pasif_function=lambda: new_deactive(),
        f='red',
        s='green',
        status=True
    )
    title_line = Frame(
        top_canvas,
        height = 2,
        background=line_color,
    )

    save_path_label = Label(
        top_canvas,
        background=color,
        fg=canvas2_text_color,
        text="Sonuçların kaydedilmesini istediğiniz klasörün yolunu giriniz:",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    path_frame = Frame(
        top_canvas,
        background=color,
        height=30
    )
    save_path = Text(
        path_frame,
        height=1,
        font=("JetBrainsMonoRoman Regular", 12),
        fg='#747474',
        background=line_color,
        border=0,
        pady=4,
        insertbackground='#c0c0c0'
    )
    browse_button = MyButton(
        path_frame,
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
        path_frame,
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
        browse_directory(text_item, w=window)
    def browse_color_change(e,c,t,b):
        b.config(background=c, text_color=t)
    def save_click(event, c, t, b):
        browse_color_change(event,c,t,b)
        placeholder_saver('cos', save_path)
    browse_button.bind("<Button-1>", lambda e: browse_click(e,'#8AB4F8','black', save_path, browse_button))
    browse_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', browse_button))
    browse_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, browse_button))
    browse_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', browse_button))
    save_button.bind("<Button-1>", lambda e: save_click(e,'#8AB4F8','black', save_button))
    save_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', save_button))
    save_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, save_button))
    save_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', save_button))

    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function('cos', save_path, placeholder)
    window.unbind("<Button-1>")
    save_path.bind("<Button-1>", lambda e: on_focus_in(e, save_path, placeholder, canvas2_text_color))
    save_path.bind("<FocusOut>", lambda e: on_focus_out(e, save_path, placeholder, canvas2_text_color))
    window.bind("<Button-1>", lambda e: on_click_outside(e, save_path, placeholder, canvas2_text_color))

    browse_button.pack(side=RIGHT, padx=(8,0))
    save_button.pack(side=RIGHT, padx=(8,0))
    save_path.pack(side=LEFT, fill=X, expand=True)

    return_list = drag_drop(0,1,0,'costupdater',
                            'Aşağıya ilgili csv dosyasini surukleyip birakiniz:',
                            bottom_canvas, window, canvas2, color, canvas2_text_color, dosyalar_dictionary, padx=0, bg_image=csv_drag_drop_image, file_image=csv_icon_image, file_type='.csv')
    drag_frame = return_list[0]

    settings_label = Label(bottom_canvas, text='Settings:', font=("JetBrainsMonoRoman Regular", 12), background=color, fg=canvas2_text_color)

    settings_height=225
    if 'costupdater2_settings.txt' not in os.listdir('Settings'):
        write_settings('Settings/costupdater2_settings.txt', costupdater2_settings_var)
    settings_text = Text(
        bottom_canvas,
        border=0,
        wrap= WORD,
        bg=line_color,
        fg='#c0c0c0',
        height = int(settings_height/15),
        font=("JetBrainsMonoRoman Regular", 10),
        insertbackground='#c0c0c0'
    )
    settings_text.bind('<Enter>',lambda e: on_text_enter(e, canvas2))
    settings_text.bind('<Leave>',lambda e: on_text_leave(e, canvas2))
    with open('Settings/costupdater2_settings.txt', 'r', encoding='utf-8') as file:
        readed = file.read()
        settings_text.insert(tk.END, readed)
        settings_text.see(tk.END)


    baslat_button = MyButton(
        bottom_canvas,
        round=15,
        width=100,
        height=50,
        text='Başlat',
        background=line_color,
        text_color='white',
        align_text='center'
    )
    def color_change(e,c,t):
        baslat_button.config(background=c, text_color=t)
    def baslat2_click(e,c,t):
        color_change(e,c,t)
        path = save_path.get(1.0, END)
        path = path.rstrip("\n")
        print("baslat2 calisti")
        output2(path)
    def baslat_click(e,c,t):
        color_change(e,c,t)
        path = save_path.get(1.0, END)
        path = path.rstrip("\n")
        print("baslat calisti")
        output(path)
    baslat_button.bind("<Button-1>", lambda e: baslat2_click(e,'#8AB4F8','black'))
    baslat_button.bind("<ButtonRelease-1>", lambda e: color_change(e,'#727478','white'))
    baslat_button.bind("<Enter>", lambda e: color_change(e,'#727478',canvas2_text_color))
    baslat_button.bind("<Leave>", lambda e: color_change(e,line_color,'white'))

    output_text = Text(
        window,
        border=0,
        wrap= WORD,
        bg=line_color,
        fg='#c0c0c0',
        height = 10,
        font=("JetBrainsMonoRoman Regular", 13),
        insertbackground='#c0c0c0'
    )
    output_text.bind("<Enter>", lambda e: on_text_enter(e, canvas2))
    output_text.bind("<Leave>", lambda e: on_text_leave(e, canvas2))

    title.pack(side='left')
    new_switch.pack(side='right')
    title_frame.grid(column=0, row=0, sticky='ew')
    title_line.grid(column=0, row=1, sticky='ew')

    top_canvas.grid(column=0, row=0, sticky='we', padx=(25,0), pady=(25,0))
    bottom_canvas.grid(column=0, row=1, sticky='we', padx=(25,0), pady=(25,0))
    save_path_label.grid(column=0, row=2, sticky='w', pady=(25,0))
    path_frame.grid(column=0, row=3, sticky='we')
    settings_label.grid(column=0, row=2, sticky='w', pady=4)
    settings_text.grid(column=0, row=3, sticky='we')
    baslat_button.grid(column=0, row=4, sticky='e', pady=(20,0))
    def output2(path):
        output_text.pack(side=BOTTOM, fill=X, padx=(canvas.winfo_width(), 0))
        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: resize(e, True))
        
        costupdater_ayarlar = settings_text.get("1.0", tk.END).rstrip("\n")
        write_settings('Settings/costupdater2_settings.txt', costupdater_ayarlar)
        
        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(output_text, "Hata: Dosya yolu algılanamadı, lütfen geçerli bir klasör seçin.", color="red")
            return
            
        csv_files = dosyalar_dictionary.get('costupdater', [])
        if not csv_files:
            text_print(output_text, "Hata: İşlenecek CSV dosyası sürüklemediniz.", color="red")
            return
            
        input_file = csv_files[0]
        
        def update_progress(msg: str):
            output_text.after(0, lambda: text_print(output_text, msg))

        def run_in_thread():
            try:
                result = process_costupdater2(
                    input_file, 
                    path, 
                    costupdater_ayarlar, 
                    progress_callback=update_progress
                )
                output_text.after(0, lambda: text_print(output_text, result["message"], color='#90EE90'))
                output_text.after(0, lambda: open_folder_in_explorer(path))
            except Exception as e:
                output_text.after(0, lambda: text_print(output_text, f"Hata: {str(e)}", color='red'))

        conversion_thread = Thread(target=run_in_thread, daemon=True)
        conversion_thread.start()

    def output(path):
        output_text.pack(side=BOTTOM, fill=X, padx=(canvas.winfo_width(), 0))
        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: resize(e, True))
        
        costupdater_ayarlar = settings_text.get("1.0", tk.END).rstrip("\n")
        write_settings('Settings/costupdater_settings.txt', costupdater_ayarlar)
        
        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(output_text, "Hata: Dosya yolu algılanamadı, lütfen geçerli bir klasör seçin.", color="red")
            return
            
        csv_files = dosyalar_dictionary.get('costupdater', [])
        if not csv_files:
            text_print(output_text, "Hata: İşlenecek CSV dosyası sürüklemediniz.", color="red")
            return
            
        input_file = csv_files[0]
        
        def update_progress(msg: str):
            output_text.after(0, lambda: text_print(output_text, msg))

        def run_in_thread():
            try:
                result = process_costupdater(
                    input_file, 
                    path, 
                    costupdater_ayarlar, 
                    progress_callback=update_progress
                )
                output_text.after(0, lambda: text_print(output_text, result["message"], color='#90EE90'))
                output_text.after(0, lambda: open_folder_in_explorer(path))
            except Exception as e:
                output_text.after(0, lambda: text_print(output_text, f"Hata: {str(e)}", color='red'))

        conversion_thread = Thread(target=run_in_thread, daemon=True)
        conversion_thread.start()

    window.bind("<Configure>", lambda e: resize(e, False))