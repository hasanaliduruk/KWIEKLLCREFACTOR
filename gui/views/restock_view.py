import tkinter as tk
from tkinter import ttk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread
import os

from utils.file_operations import browse_directory, placeholder_saver, path_text_function, write_settings, save_location_saver
from utils.event_handlers import on_focus_in, on_focus_out, on_click_outside, on_mouse_wheel, on_text_enter, on_text_leave
from utils.gui_helpers import width_f
from gui.components.custom_buttons import MyButton
from gui.components.scrollbar import MyScrollbar
from gui.components.drag_drop import drag_drop, ham_drag_drop2
from gui.components.custom_buttons import SwitchButton
from gui.views.futureprice_view import render_futureprice_view


from tkinter import PhotoImage
import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread

settings_var = (
    "upc = UPC, upc, Upc, UPC #\n"
    "brand = BRAND, Brand, brand\n"
    "price = NET_AMOUNT, Price, price\n"
    "case = CASEPACK, Size, Case, case, size\n"
    "Quantity on hand = Qty on Hand, Quantity Available\n"
    "pk = PK\n"
    "======================================\n"
    "41 cost: 0.78\n"
    "41 standart: 0.78\n"
    "45 cost: 0.78\n"
    "45 standart: 0.78\n"
    "19 cost: 0.78\n"
    "19 standart: 0.78\n"
    "27 cost: 1.10\n"
    "27 standart: 1.10\n"
    "18 cost: 1.10\n"
    "18 standart: 1.10\n"
    "01 cost: 1.10\n"
    "01 standart: 1.10\n"
    "NF: 0.78")

def start_excel_editor_thread(ham_liste,export_liste,restock_liste,path,islem, restock_output, save_name, progress):
    t = Thread(target=rest, args=(path, ham_liste, export_liste, restock_liste, islem, progress, restock_output, save_name), daemon=True)
    t.start()


def render_restock_view(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, resize_dictionary, active_dictionary, main_frame_resize):
    global restock_submit_button
    global restock_inner_frame
    global restock_main_scrollbar
    global restock_output

    def on_resize(e):
        scale = main_frame_resize()
        canvas2.config(scrollregion=canvas2.bbox('all'))
        item_list = [ham_surukle_text, export_surukle_text, restock_surukle_text]
        ust_list = [restock_question, export_question, file_path]

        for item in item_list:
            item.config(font=("JetBrainsMonoRoman Regular", round(9*scale)))
        ham_main_canvas.config(height=175*scale)
        export_main_canvas.config(height=175*scale)
        restock_main_canvas.config(height=175*scale)
        alt_canvas_uzaklik = alt_canvas.winfo_y()
        p = alt_canvas_uzaklik + alt_canvas.winfo_height()
        if canvas2.winfo_width() < resize_dictionary[restock_inner_frame]['width']*scale:
            frame_width = canvas2.winfo_width()
        else:
            frame_width = resize_dictionary[restock_inner_frame]['width']*scale
        if frame_width < 1000:
            frame_width = 1000
        if p+55 > canvas2.winfo_height():
            restock_inner_frame.configure(height=p+55, width=frame_width)
        else:
            restock_inner_frame.configure(height=canvas2.winfo_height(), width=frame_width)



    settings_height = 250
    if 'restock_settings.txt' not in os.listdir('Settings'):
        write_settings('Settings/restock_settings.txt', settings_var)


    def restock_builder(a,height):
        active_dictionary['restock'] = 1
        if active_dictionary['export'] == 0:
            active_dictionary['export'] = 1
            export_question_switch.pasif()
        a = active_dictionary['restock'] + active_dictionary['export']
        updater()


    def restock_destroyer():
        active_dictionary['restock'] = 0
        a = active_dictionary['restock'] + active_dictionary['export']
        #alt_canvas.configure(height=(a+1)*height+25*(a+1))
        #alt_canvas.update()
        try:
            restock_surukle_text.grid_forget()
            restock_main_canvas.grid_forget()
        except:
            pass
        updater()

    def export_builder(a,height):
        active_dictionary['export'] = 1
        a = active_dictionary['restock'] + active_dictionary['export']
        updater()

    def export_destroyer():
        active_dictionary['export'] = 0
        if active_dictionary['restock'] == 1:
            active_dictionary['restock'] = 0
            restock_question_switch.active()
        a = active_dictionary['restock'] + active_dictionary['export']

        #alt_canvas.configure(height=(a+1)*height+25*(a+1))
        #alt_canvas.update()
        try:
            export_surukle_text.grid_forget()
            export_main_canvas.grid_forget()
            restock_surukle_text.grid_forget()
            restock_main_canvas.grid_forget()
        except:
            pass
        updater()
    def updater():
        a = active_dictionary['export'] + active_dictionary['restock']
        restock_submit_button.grid(column=1, row=11, padx=(10,25), pady=10, sticky='e')
        future_price_button.grid(column=0, row=11, pady=10, sticky='e')

        if active_dictionary['export'] == 1:
            export_main_canvas.grid(column = 0, row = 5, columnspan=2, sticky='nwes', padx=25)
            export_surukle_text.grid(column=0, row=4, columnspan=2, padx=25, pady=10, sticky='w')


        if active_dictionary['restock'] == 1:
            restock_main_canvas.grid(column = 0, row = 7, columnspan=2, sticky='nwes', padx=25)
            restock_surukle_text.grid(column=0, row=6, columnspan=2, padx=25, pady=10, sticky='w')


        alt_canvas.config(height=restock_settings.winfo_y()+restock_settings.winfo_height()+100)
        alt_canvas.update()
        p = alt_canvas.winfo_y() + alt_canvas.winfo_height()

        if p+55 > canvas2.winfo_height():
            restock_inner_frame.configure(height=p+55)
        else:
            restock_inner_frame.configure(height=canvas2.winfo_height())

    restock_inner_frame = Frame(canvas2, bg=color, height= canvas2.winfo_height(), width=0)
    restock_inner_frame.grid_columnconfigure(0, weight=1)
    restock_inner_frame.grid_propagate(False)
    canvas2.create_window((0, 0), window=restock_inner_frame, anchor="nw")
    #resize_liste.append([0,0,600,900,restock_inner_frame])
    restock_main_scrollbar = MyScrollbar(window, target=canvas2, command=canvas2.yview, thumb_thickness=8, thumb_color='#888888', thickness=18, line_color=line_color)
    restock_main_scrollbar.pack(side= RIGHT, fill=tk.Y)
    canvas2.configure(yscrollcommand=restock_main_scrollbar.set)

    canvas2.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas2))
    #bg='#ADD8E6'
    alt_canvas = Canvas(
        restock_inner_frame,
        height=int(0),
        width=int(canvas2.winfo_width()),
        borderwidth=0, highlightthickness=0,
        bg=color, highlightbackground=color,
    )
    alt_canvas.grid_columnconfigure(0, weight=1)
    height = int(150)

    width = int(650)
    ham_liste = ham_drag_drop2(row1=0,row=1,column=0,dict_name='ham_dosyalar_liste',text="Ham dosyalarin excellerini asagiya surukleyip birakiniz:", parent=alt_canvas,
                               window=window, canvas2=canvas2, color=color, text_color=canvas2_text_color, dosyalar_dictionary=dosyalar_dictionary)
    ham_main_canvas= ham_liste[0]
    ham_surukle_text = ham_liste[1]
    export_liste = drag_drop(row1=2,row=3,column=0,dict_name='export_dosyalar_liste',text="Export dosyalarin excellerini asagiya surukleyip birakiniz:", parent=alt_canvas,
                             window=window, canvas2=canvas2, color=color, text_color=canvas2_text_color, dosyalar_dictionary=dosyalar_dictionary)
    export_main_canvas= export_liste[0]
    export_surukle_text = export_liste[1]
    restock_liste = drag_drop(row1=4,row=5,column=0,dict_name='restock_dosyalar_liste',text="Restock excelini asagiya surukleyip birakiniz:", parent=alt_canvas, 
                              window=window, canvas2=canvas2, color=color, text_color=canvas2_text_color, dosyalar_dictionary=dosyalar_dictionary)
    restock_main_canvas= restock_liste[0]
    restock_surukle_text = restock_liste[1]
    a = 1
    alt_canvas.configure(height= height*4+settings_height+25)
    alt_canvas.update()

    settings_label = Label(alt_canvas, text='Settings:', font=("JetBrainsMonoRoman Regular", 12), background=color, fg=canvas2_text_color)
    settings_label.grid(column=0, row=9, columnspan=2, sticky = 'w', padx=25, pady=3)
    restock_settings = Text(alt_canvas,insertbackground='#c0c0c0', border=0, wrap= WORD,width=int(width_f(650, canvas2)), bg=line_color, fg='#c0c0c0', height = int(settings_height/15),font=("JetBrainsMonoRoman Regular", 10))
    restock_settings.grid(column=0, row=10, columnspan=2, sticky = 'we', padx=25, pady=5)
    #restock_settings.place(x=25, y=(0+1)*height+25*(0+1))
    restock_settings.bind('<Enter>',lambda e: on_text_enter(e, canvas2))
    restock_settings.bind('<Leave>',lambda e: on_text_leave(e, canvas2))




    with open('Settings/restock_settings.txt', 'r', encoding='utf-8') as file:
        readed = file.read()
        restock_settings.insert(tk.END, readed)
        restock_settings.see(tk.END)
    alt_canvas.update()
    ust_canvas = Canvas(restock_inner_frame, background=color, highlightthickness=0)
    pad = 35
    options_frame = Frame(
        ust_canvas,
        bg=line_color,
        width = 450,
        height=142,
    )
    options_frame.grid_propagate(False)
    options_frame.grid_columnconfigure(0, weight=1)
    restock_option_frame = Frame(
        options_frame,
        bg=line_color,
        height=70
    )
    restock_option_frame.pack_propagate(False)
    restock_option_frame.grid(column=0, row=0, sticky='we')
    restock_question = Label(
        restock_option_frame,
        text='Restock',
        background=line_color,
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12)
    )
    restock_question_switch = SwitchButton(
        parent = restock_option_frame,
        active_function= lambda: restock_builder(a, height),
        pasif_function= lambda: restock_destroyer(),
        border=0,
        highlightthickness=0,
        f='red',
        s='green',
        status=True
    )
    restock_question.pack(side='left', padx=(15, 0))
    restock_question_switch.pack(side='right', padx=(0, 15))

    line_1 = Frame(
        options_frame,
        height=2,
        bg='#79918B'
    )
    line_1.grid(column=0, row=1, sticky='we')

    export_option_frame = Frame(
        options_frame,
        bg=line_color,
        height=70
    )
    export_option_frame.pack_propagate(False)
    export_option_frame.grid(column=0, row=2, sticky='we')
    export_question = Label(
        export_option_frame,
        text='Export',
        background=line_color,
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12)
    )
    export_question_switch = SwitchButton(
        parent = export_option_frame,
        active_function= lambda: export_builder(a, height),
        pasif_function= lambda: export_destroyer(),
        border=0,
        highlightthickness=0,
        f='red',
        s='green',
        status=True
    )
    export_question.pack(side='left', padx=(15, 0))
    export_question_switch.pack(side='right', padx=(0, 15))

    welcome_text = Label(
        ust_canvas,
        background=color,
        text="RESTOCK PROGRAMI",
        font=("JetBrainsMonoRoman Regular", 24 * -1),
        fg=canvas2_text_color,
    )
    welcome_line = Frame(
        ust_canvas,
        background=line_color,
        height=2
    )
    file_path = Label(
        ust_canvas,
        text= 'Aşağıya sonuçların kaydedilmesini istediğiniz dosya yolunu giriniz:',
        background=color,
        font=("JetBrainsMonoRoman Regular", 12),
        fg=canvas2_text_color,
    )
    browse_frame = Frame(ust_canvas, bg=color, height=30)
    save_path_text = Text(
        browse_frame,
        height=1,
        border=0,
        fg='#747474',
        bg=line_color,
        font=("JetBrainsMonoRoman Regular", 12),
        pady=4,
        insertbackground='#c0c0c0')
    browse_button = MyButton(
        browse_frame,
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
        browse_frame,
        text='Kaydet',
        background=line_color,
        text_color='white',
        width=100,
        height=25,
        round=0,
        align_text="center",
        font=("Helvatica", 9)
    )
    save_name_label = Label(
        ust_canvas,
        text= 'Aşağıya sonucun kaydedilmesini istediginiz ismi giriniz:',
        background=color,
        font=("JetBrainsMonoRoman Regular", 12),
        fg=canvas2_text_color,
    )
    save_name_text = Text(
        ust_canvas,
        height=1,
        border=0,
        fg=canvas2_text_color,
        bg=line_color,
        font=("JetBrainsMonoRoman Regular", 12),
        pady=4,
        insertbackground='#c0c0c0')

    def browse_click(event, c, t, text_item, b):
        browse_color_change(event,c,t,b)
        browse_directory(text_item, w=window)
    def browse_color_change(e,c,t,b):
        b.config(background=c, text_color=t)
    def save_click(event, c, t, b):
        browse_color_change(event,c,t,b)
        placeholder_saver('res', save_path_text)
    browse_button.bind("<Button-1>", lambda e: browse_click(e,'#8AB4F8','black', save_path_text, browse_button))
    browse_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', browse_button))
    browse_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, browse_button))
    browse_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', browse_button))
    save_button.bind("<Button-1>", lambda e: save_click(e,'#8AB4F8','black', save_button))
    save_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', save_button))
    save_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, save_button))
    save_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', save_button))


    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function('res', save_path_text, placeholder, save_name_text)
    window.unbind("<Button-1>")
    save_path_text.bind("<Button-1>", lambda e: on_focus_in(e, save_path_text, placeholder, canvas2_text_color))
    save_path_text.bind("<FocusOut>", lambda e: on_focus_out(e, save_path_text, placeholder, canvas2_text_color))
    window.bind("<Button-1>", lambda e: on_click_outside(e, save_path_text, placeholder, canvas2_text_color))
    browse_frame.pack_propagate(False)
    browse_button.pack(side=RIGHT, padx=(8,0))
    save_button.pack(side=RIGHT, padx=(8,0))
    save_path_text.pack(side=LEFT, fill=X, expand=True)


    ust_canvas.grid_columnconfigure(0, weight=1)
    welcome_text.grid(column=0, row=0, sticky='w', padx=(25,0), pady=(20,0))
    welcome_line.grid(column=0, row=1, sticky='we', padx=(25,0))
    options_frame.grid(column=0, row=2, sticky='w', padx=(25,0), pady=(20,15))
    file_path.grid(column=0, row=6, sticky='w', padx=(25,0), pady=(12,3))
    browse_frame.grid(column=0, row=7, sticky='we', padx=(25, 275))
    save_name_label.grid(column=0, row=8, sticky='w', padx=(25,0), pady=(12,3))
    save_name_text.grid(column=0, row=9, sticky='we', padx=(25, 275))
    ust_canvas.grid(column=0,row=0,sticky='we')




    restock_inner_frame.bind("<Configure>", lambda e: canvas2.config(scrollregion=canvas2.bbox("all")))
    restock_inner_frame.configure(height=canvas2.winfo_height())
    restock_inner_frame.update()

    restock_output = Text(
        window,
        border=0,
        wrap= WORD,
        bg=line_color,
        fg='#c0c0c0',
        height = 10,
        font=("JetBrainsMonoRoman Regular", 13),
        insertbackground='#c0c0c0'
    )
    restock_output.bind('<Enter>', lambda e: on_text_enter(e, canvas2))
    restock_output.bind('<Leave>', lambda e: on_text_leave(e, canvas2))

    global progress
    progress = ttk.Progressbar(window, orient=tk.HORIZONTAL, mode='determinate')

    def print_liste(restock_settings, path):
        color_change(1,'#8AB4F8','black', restock_submit_button)
        def submit_resize(event):
            scale = main_frame_resize()
            item_list = [ham_surukle_text, export_surukle_text, restock_surukle_text]
            ust_list = [save_path_text, restock_question, export_question, file_path]

            for item in item_list:
                item.config(font=("JetBrainsMonoRoman Regular", round(9*scale)))
            ham_main_canvas.config(height=175*scale)
            export_main_canvas.config(height=175*scale)
            restock_main_canvas.config(height=175*scale)
            for item in ust_list:
                item.config(font=("JetBrainsMonoRoman Regular", round(9*scale)))
            restock_output.pack(side=BOTTOM, fill=X, padx=(canvas.winfo_width(),0))
            restock_output.config(font=("JetBrainsMonoRoman Regular", round(9*scale)))
            restock_output.update_idletasks()
            try:
                progress.pack_configure(padx=(canvas.winfo_width(),0))
            except:pass
            alt_canvas_uzaklik = alt_canvas.winfo_y() + 250
            p = alt_canvas_uzaklik + alt_canvas.winfo_height()
            if canvas2.winfo_width() < resize_dictionary[restock_inner_frame]['width']*scale:
                frame_width = canvas2.winfo_width()
            else:
                frame_width = resize_dictionary[restock_inner_frame]['width']*scale
            if frame_width < 1000:
                frame_width = 1000
            if p+55 > canvas2.winfo_height():
                restock_inner_frame.configure(height=p+55, width=frame_width)
            else:
                restock_inner_frame.configure(height=canvas2.winfo_height(), width=frame_width)

        n_ham_dosyalar_liste = []
        n_export_dosyalar_liste = []
        n_restock_dosyalar_liste = []
        try:
            for i in dosyalar_dictionary['ham_dosyalar_liste']:
                if i[0] == ' ':
                    i = i.replace(' ','',1)
                n_ham_dosyalar_liste.append(i)
        except:pass
        try:
            for i in dosyalar_dictionary['export_dosyalar_liste']:
                if i[0] == ' ':
                    i = i.replace(' ','',1)
                n_export_dosyalar_liste.append(i)
        except:pass
        try:
            for i in dosyalar_dictionary['restock_dosyalar_liste']:
                if i[0] == ' ':
                    i = i.replace(' ','',1)
                n_restock_dosyalar_liste.append(i)
        except:pass
        restock_ayarlar = restock_settings.get("1.0", tk.END)
        restock_ayarlar = restock_ayarlar.rstrip("\n")
        write_settings('Settings/restock_settings.txt', restock_ayarlar)
        save_name = save_name_text.get(1.0, tk.END).strip('\n')
        save_location_saver('res', save_name_text)
        path = path.replace('\n','')

        restock_output.pack(side=BOTTOM, fill=X, padx=(canvas.winfo_width(),0))

        progress.pack_forget()
        progress.pack(side=BOTTOM, fill=X, padx=(canvas.winfo_width(),0))

        if path != "Example: C:/Users/Username/Desktop/sonuc":
            start_excel_editor_thread(n_ham_dosyalar_liste,n_export_dosyalar_liste,n_restock_dosyalar_liste,path,active_dictionary,restock_output, save_name, progress)
        else:
            restock_output.insert(END, 'dosya yolunu dogru girdiginizden emin olun ve tekrar deneyin...\n')
            restock_output.see(END)
        window.unbind('<Configure>')
        submit_resize(1)
        window.bind('<Configure>', submit_resize)



    restock_submit_button = MyButton(
        alt_canvas,
        round=15,
        width=100,
        height=50,
        text='Başlat',
        background=line_color,
        text_color='white',
        align_text='center'
    )
    future_price_button = MyButton(
        alt_canvas,
        round=15,
        width=150,
        height=50,
        text='Future Price',
        background=line_color,
        text_color='white',
        align_text='center'
    )
    def color_change(e,c,t, b):
        b.config(background=c, text_color=t)
    restock_submit_button.bind('<Button-1>', lambda e: print_liste(restock_settings, save_path_text.get(1.0, END)))
    restock_submit_button.bind("<ButtonRelease-1>", lambda e: color_change(e,'#727478','white', restock_submit_button))
    restock_submit_button.bind("<Enter>", lambda e: color_change(e,'#727478',canvas2_text_color, restock_submit_button))
    restock_submit_button.bind("<Leave>", lambda e: color_change(e,line_color,'white', restock_submit_button))





    future_price_button.bind('<Button-1>', lambda e: render_futureprice_view(future_price_button, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary))
    future_price_button.bind("<ButtonRelease-1>", lambda e: color_change(e,'#727478','white', future_price_button))
    future_price_button.bind("<Enter>", lambda e: color_change(e,'#727478',canvas2_text_color, future_price_button))
    future_price_button.bind("<Leave>", lambda e: color_change(e,line_color,'white', future_price_button))

    restock_inner_frame.update()
    alt_canvas.grid(column=0, row=1, sticky='we', padx=(0,300))

    window.update_idletasks()

    #window.update_idletasks()
    updater()
    resize_dictionary[restock_inner_frame] = {'width': canvas2.winfo_width(), 'height': restock_inner_frame.winfo_height()}
    resize_dictionary[alt_canvas] = {'width': alt_canvas.winfo_width(), 'height': alt_canvas.winfo_height(), 'x': alt_canvas.winfo_x(), 'y': alt_canvas.winfo_y()}







    window.unbind('<Configure>')
    on_resize(1)
    window.bind('<Configure>', lambda e: on_resize(e))