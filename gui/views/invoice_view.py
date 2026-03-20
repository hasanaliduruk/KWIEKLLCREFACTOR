import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
import os

from utils.file_operations import browse_directory, placeholder_saver, path_text_function, write_settings
from utils.event_handlers import on_focus_in, on_focus_out, on_click_outside, on_mouse_wheel, on_text_enter, on_text_leave
from utils.gui_helpers import text_print, open_folder_in_explorer
from gui.components.drag_drop import drag_drop
from gui.components.custom_buttons import MyButton
from gui.components.scrollbar import MyScrollbar
from core.invoice_processor import process_invoice


import tkinter as tk
from tkinter import Canvas, Frame, Label, Text, WORD, BOTTOM, X, RIGHT, LEFT, BOTH, END
from threading import Thread

invoice_settings_var = (
    'remove = Status, QuantityNotShipped, InvalidReason\n'
    'shipquantity = ShipQuantity\n'
    'date = InvoiceDate'
)

def render_invoice_view(canvas, canvas2, main_frame_resize, window, color, line_color, canvas2_text_color, dosyalar_dictionary,
                    selected_image, not_selected_image, csv_drag_drop_image, csv_icon_image):
    def resize(e, a):
        scale = main_frame_resize()
        drag_frame.config(height=175*scale)
        height = bottom_canvas.winfo_y()+bottom_canvas.winfo_height()+20
        if a:
            output_text.pack_configure(padx=(canvas.winfo_width(), 0))
            if height < canvas2.winfo_height()-200:
                invoice_main_frame.config(width=750*scale, height=canvas2.winfo_height())
            else:
                invoice_main_frame.config(width=750*scale, height=height+200)
        else:
            if height < canvas2.winfo_height():
                invoice_main_frame.config(width=750*scale, height=canvas2.winfo_height())
            else:
                invoice_main_frame.config(width=750*scale, height=height)
        canvas2.config(scrollregion=canvas2.bbox("all"))
    invoice_active_dictionary= {
        '0': 1,
    }
    def invoice_builder():
        invoice_active_dictionary['0'] = 1
        invoice_yes.configure(image=selected_image)
        invoice_no.configure(image=not_selected_image)


    def invoice_destroyer():
        invoice_active_dictionary['0'] = 0
        invoice_yes.configure(image=not_selected_image)
        invoice_no.configure(image=selected_image)

    invoice_main_frame = Frame(
        canvas2,
        background=color,
        width=750,
        height=canvas2.winfo_height()
    )
    invoice_main_frame.grid_propagate(False)
    invoice_main_frame.grid_columnconfigure(0, weight=1)
    canvas2.create_window((0,0), window=invoice_main_frame, anchor='nw')
    canvas2.bind_all('<MouseWheel>', lambda e: on_mouse_wheel(e, canvas2))
    invoice_scrollbar = MyScrollbar(window, target=canvas2, command=canvas2.yview, thumb_thickness=8, thumb_color='#888888', thickness=18, line_color=line_color)
    canvas2.config(yscrollcommand=invoice_scrollbar.set, scrollregion=canvas2.bbox('all'))
    invoice_scrollbar.pack(side=RIGHT, fill=tk.Y)
    top_canvas = Canvas(
        invoice_main_frame,
        border=0,
        highlightthickness=0,
        background=color
    )
    top_canvas.grid_columnconfigure(0, weight=1)
    bottom_canvas = Canvas(
        invoice_main_frame,
        border=0,
        highlightthickness=0,
        background=color
    )
    bottom_canvas.grid_columnconfigure(0, weight=1)
    invoice_title = Label(
        top_canvas,
        background=color,
        text="Invoice Program",
        font=(("JetBrainsMonoRoman Regular", 24 * -1)),
        fg=canvas2_text_color
    )
    invoice_title_line = Frame(
        top_canvas,
        height=2,
        background=line_color
    )
    invoice_cevap = Frame(top_canvas, bg=color)
    invoice_yes = tk.Button(
        invoice_cevap,
        image = selected_image,
        relief='sunken',
        border = 0,
        background=color,
        activebackground=color,
        text='Evet',
        compound='left',
        fg=canvas2_text_color,
        activeforeground=canvas2_text_color,
        cursor='hand2',
        padx=5,
        font=("JetBrainsMonoRoman Regular", 12),
        command= lambda: invoice_builder()
    )
    #restock_yes.image = not_selected_image

    invoice_no = tk.Button(
        invoice_cevap,
        image = not_selected_image,
        relief='sunken',
        background=color,
        activebackground=color,
        border = 0,
        text='Hayır',
        compound='left',
        fg=canvas2_text_color,
        activeforeground=canvas2_text_color,
        cursor='hand2',

        font=("JetBrainsMonoRoman Regular", 12),
        padx=5,
        command= lambda: invoice_destroyer()
    )
    invoice_yes.pack(side=LEFT, padx=15)
    invoice_no.pack(side=LEFT)
    #restock_no.image = selected_image
    invoice_question = Label(
        top_canvas,
        text='0\'lari silmek istiyor musun?',
        background=color,
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 12)
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
        browse_directory(text_item , w=window)
    def browse_color_change(e,c,t,b):
        b.config(background=c, text_color=t)
    def save_click(event, c, t, b):
        browse_color_change(event,c,t,b)
        placeholder_saver('inv', save_path)
    browse_button.bind("<Button-1>", lambda e: browse_click(e,'#8AB4F8','black', save_path, browse_button))
    browse_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', browse_button))
    browse_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, browse_button))
    browse_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', browse_button))
    save_button.bind("<Button-1>", lambda e: save_click(e,'#8AB4F8','black', save_button))
    save_button.bind("<ButtonRelease-1>", lambda e: browse_color_change(e,'#727478','white', save_button))
    save_button.bind("<Enter>", lambda e: browse_color_change(e,'#727478',canvas2_text_color, save_button))
    save_button.bind("<Leave>", lambda e: browse_color_change(e,line_color,'white', save_button))

    placeholder = "Example: C:/Users/Username/Desktop/sonuc"
    path_text_function('inv', save_path, placeholder)
    window.unbind("<Button-1>")
    save_path.bind("<Button-1>", lambda e: on_focus_in(e, save_path, placeholder, canvas2_text_color))
    save_path.bind("<FocusOut>", lambda e: on_focus_out(e, save_path, placeholder, canvas2_text_color))
    window.bind("<Button-1>", lambda e: on_click_outside(e, save_path, placeholder, canvas2_text_color))

    browse_button.pack(side=RIGHT, padx=(8,0))
    save_button.pack(side=RIGHT, padx=(8,0))
    save_path.pack(side=LEFT, fill=X, expand=True)

    return_list = drag_drop(0,1,0,'invoice_csv',
              'Aşağıya invoice csv dosyalarını sürükleyip bırakınız:',
              bottom_canvas, padx=0, bg_image=csv_drag_drop_image, file_image=csv_icon_image, file_type='.csv',
              window=window, canvas2=canvas2, color=color, text_color=canvas2_text_color, dosyalar_dictionary=dosyalar_dictionary)
    drag_frame = return_list[0]

    settings_label = Label(bottom_canvas, text='Settings:', font=("JetBrainsMonoRoman Regular", 12), background=color, fg=canvas2_text_color)

    settings_height=150
    if 'invoice_settings.txt' not in os.listdir('Settings'):
        write_settings('Settings/invoice_settings.txt', invoice_settings_var)
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
    with open('Settings/invoice_settings.txt', 'r', encoding='utf-8') as file:
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
    def baslat_click(e,c,t):
        color_change(e,c,t)
        path = save_path.get(1.0, END)
        path = path.rstrip("\n")
        output(path)
    baslat_button.bind("<Button-1>", lambda e: baslat_click(e,'#8AB4F8','black'))
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


    top_canvas.grid(column=0, row=0, sticky='we', padx=(25,0), pady=(25,0))
    bottom_canvas.grid(column=0, row=1, sticky='we', padx=(25,0), pady=(25,0))
    invoice_title.grid(column=0, row=0, sticky='w')
    invoice_title_line.grid(column=0, row=1, sticky='we')
    invoice_question.grid(column=0, row=2, sticky='w', padx=(0,0))
    invoice_cevap.grid(column=0, row=3, sticky='w', padx=(0,0), pady=(5, 0))
    save_path_label.grid(column=0, row=4, sticky='w', pady=(25,0))
    path_frame.grid(column=0, row=5, sticky='we')
    settings_label.grid(column=0, row=2, sticky='w', pady=4)
    settings_text.grid(column=0, row=3, sticky='we')
    baslat_button.grid(column=0, row=4, sticky='e', pady=(20,0))
    def output(path):
        output_text.pack(side=tk.BOTTOM, fill=tk.X, padx=(canvas.winfo_width(), 0))
        window.unbind("<Configure>")
        window.bind("<Configure>", lambda e: resize(e, True))
        
        invoice_ayarlar = settings_text.get("1.0", tk.END).rstrip("\n")
        write_settings('Settings/invoice_settings.txt', invoice_ayarlar)
        delzero = invoice_active_dictionary["0"]
        
        if path == "Example: C:/Users/Username/Desktop/sonuc" or path == "":
            text_print(output_text, "Hata: Dosya yolu algılanamadı, lütfen geçerli bir klasör seçin.", color="red")
            return
            
        csv_files = dosyalar_dictionary.get('invoice_csv', [])
        if not csv_files:
            text_print(output_text, "Hata: İşlenecek CSV dosyası sürüklemediniz.", color="red")
            return

        def update_progress(msg: str):
            output_text.after(0, lambda: text_print(output_text, msg))

        def run_in_thread():
            try:
                result = process_invoice(
                    csv_files, 
                    path, 
                    invoice_ayarlar, 
                    delzero,
                    progress_callback=update_progress
                )
                output_text.after(0, lambda: text_print(output_text, result["message"], color='#90EE90'))
                output_text.after(0, lambda: open_folder_in_explorer(os.path.dirname(result["output_path"])))
            except Exception as e:
                output_text.after(0, lambda: text_print(output_text, f"Hata: {str(e)}", color='red'))

        conversion_thread = Thread(target=run_in_thread, daemon=True)
        conversion_thread.start()
    window.bind("<Configure>", lambda e: resize(e, False))