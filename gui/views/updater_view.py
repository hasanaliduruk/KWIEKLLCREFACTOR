import tkinter as tk
from tkinter import Frame, Label, ttk
from threading import Thread

from gui.components.custom_buttons import MyButton



def render_updater_view(canvas2, color, window, line_color, canvas2_text_color, CURRENT_VERSION, is_connected):
    checkforupdates_label = Label(
        canvas2,
        text='Güncellemeleri kontrol etmek için Check For Updates butonuna tıklayın:',
        font=("JetBrainsMonoRoman Regular", 12),
        bg=color,
        fg=canvas2_text_color
    )
    checkforupdates = MyButton(
        canvas2,
        round=5,
        width=150,
        height=45,
        text='Check For Updates',
        background=line_color,
        text_color='white',
        align_text='center'
    )
    doyouwanna_frame = Frame(
        canvas2,
        bg=color,
    )
    doyouwanna_label = Label(
        doyouwanna_frame,
        bg=color,
        fg=canvas2_text_color,
        text="Yeni bir güncelleme bulundu! Yüklemek istiyor musun?",
        font=("JetBrainsMonoRoman Regular", 12),
    )
    release_notes = MyButton(
        doyouwanna_frame,
        round=5,
        width=125,
        height=30,
        text="Release Notes",
        background=line_color,
        text_color='white',
        align_text='center'
    )
    yes_button = MyButton(
        doyouwanna_frame,
        round=5,
        width=75,
        height=30,
        text='Yükle',
        background=line_color,
        text_color='white',
        align_text='center'
    )
    yes_button.bind("<ButtonRelease-1>", lambda e: color_change(e,'#727478','white', yes_button))
    yes_button.bind("<Enter>", lambda e: color_change(e,'#727478',canvas2_text_color, yes_button))
    yes_button.bind("<Leave>", lambda e: color_change(e,line_color,'white', yes_button))
    release_notes.bind("<ButtonRelease-1>", lambda e: color_change(e,'#727478','white', release_notes))
    release_notes.bind("<Enter>", lambda e: color_change(e,'#727478',canvas2_text_color, release_notes))
    release_notes.bind("<Leave>", lambda e: color_change(e,line_color,'white', release_notes))
    doyouwanna_frame.grid_columnconfigure(0, weight=1)
    doyouwanna_label.grid(column=0, row=0, stick='w')
    release_notes.grid(column=0, row=1, stick='e', padx=(0, 5))
    yes_button.grid(column=1, row=1, stick='e')
    progress_label = Label(window, bg=color, fg=canvas2_text_color, text="İndiriliyor...")
    progress_bar = ttk.Progressbar(window, orient="horizontal", mode='determinate')
    def is_connected_starter(CURRENT_VERSION, progress_bar, progress_label, doyouwanna_frame, doyouwanna_label, yes_button, release_notes):
        t = Thread(target=is_connected, args=(CURRENT_VERSION, progress_bar, progress_label, doyouwanna_frame, doyouwanna_label, yes_button, release_notes), daemon=True)
        t.start()
    def color_change(e,c,t,i):
        i.config(background=c, text_color=t)
    def baslat_click(e,c,t,i):
        color_change(e,c,t,i)
        is_connected_starter(CURRENT_VERSION, progress_bar, progress_label, doyouwanna_frame, doyouwanna_label, yes_button, release_notes)
    checkforupdates.bind("<Button-1>", lambda e: baslat_click(e,'#8AB4F8','black', checkforupdates))
    checkforupdates.bind("<ButtonRelease-1>", lambda e: color_change(e,'#727478','white', checkforupdates))
    checkforupdates.bind("<Enter>", lambda e: color_change(e,'#727478',canvas2_text_color, checkforupdates))
    checkforupdates.bind("<Leave>", lambda e: color_change(e,line_color,'white', checkforupdates))
    canvas2.grid_columnconfigure(0, weight=1)
    checkforupdates_label.grid(column=0, row=0, sticky='w')
    canvas2.update_idletasks()
    checkforupdates.grid(column=0, row=1, padx=(checkforupdates_label.winfo_width()-150,0), pady=(10,0), sticky='w')
