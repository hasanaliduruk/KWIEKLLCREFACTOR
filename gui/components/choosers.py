import tkinter as tk
from gui.components.option_menu import CustomOptionMenu
from gui.components.custom_buttons import MyButton
from utils.event_handlers import on_focus_in, on_focus_out, on_click_outside
from utils.file_operations import browse_directory

class ConvertChooser(tk.Frame):
    def __init__(self, window, parent, down_arrow, var1: tk.StringVar, var2: tk.StringVar,cursor='hand2', pady=10, padx=0, color='#202124', canvas2_text_color='#E3E3E3', line_color='#3F4042'):
        super().__init__(parent, bg=parent.cget("bg"), padx=padx, pady=pady)

        self.var1 = var1
        self.var2 = var2
        self.options1 = ["csv", "xlsx", "txt"]
        self.options2 = ["xlsx", "txt"]
        self.var1.trace_add("write", self.var1_changed)


        convert_label = tk.Label(
            self,
            background=color,
            fg=canvas2_text_color,
            text="convert",
            font=("JetBrainsMonoRoman Regular", 12)
        )
        convert_first_frame = tk.Frame(self, background=color, highlightthickness=2, highlightbackground=line_color, highlightcolor=line_color)
        convert_option_first = tk.Button(
            convert_first_frame,
            cursor=cursor,
            image=down_arrow,
            relief="sunken",
            borderwidth=2,
            border=0,
            textvariable=self.var1,
            compound='right',
            padx=10,
            font=("JetBrainsMonoRoman Regular", 12),
            activebackground=color,
            activeforeground=canvas2_text_color,
            command=lambda: self.on_button_click(self.option_menu_first),
            highlightthickness=1,
            highlightbackground=line_color,
            highlightcolor=line_color,
            bg=color,
            fg=canvas2_text_color
        )
        convert_option_first.image = down_arrow
        self.option_menu_first = CustomOptionMenu(
            window, convert_first_frame, self.options1, convert_option_first,
            cursor=cursor,
            var=self.var1,
            background_color=color,
            outline_color=line_color,
            foreground_color=canvas2_text_color,
            on_enter_fg=canvas2_text_color,
            on_enter_color=line_color

        )
        to_label = tk.Label(
            self,
            background=color,
            fg=canvas2_text_color,
            text="to",
            font=("JetBrainsMonoRoman Regular", 12)
        )
        convert_second_frame = tk.Frame(self, background=color, highlightthickness=2, highlightbackground=line_color, highlightcolor=line_color)
        convert_option_second = tk.Button(
            convert_second_frame,
            cursor=cursor,
            image=down_arrow,
            relief="sunken",
            borderwidth=2,
            border=0,
            textvariable=self.var2,
            compound='right',
            padx=10,
            font=("JetBrainsMonoRoman Regular", 12),
            activebackground=color,
            activeforeground=canvas2_text_color,
            command=lambda:self.on_button_click(self.option_menu_second),
            highlightthickness=1,
            highlightbackground=line_color,
            highlightcolor=line_color,
            bg=color,
            fg=canvas2_text_color
        )
        convert_option_second.image = down_arrow

        self.option_menu_second = CustomOptionMenu(
            window, convert_second_frame, self.options2, convert_option_second,
            cursor=cursor,
            var=self.var2,
            background_color=color,
            outline_color=line_color,
            foreground_color=canvas2_text_color,
            on_enter_fg=canvas2_text_color,
            on_enter_color=line_color
        )
        convert_label.pack(side=tk.LEFT)
        convert_first_frame.pack(side=tk.LEFT)
        convert_option_first.pack()
        to_label.pack(side=tk.LEFT)
        convert_second_frame.pack(side=tk.LEFT)
        convert_option_second.pack(side=tk.LEFT)
    def on_button_click(self, option_menu):
        option_menu.toggle()
    def var1_changed(self, *args):
        global previus_value
        #print(previus_value)
        new_value = self.var1.get()
        if previus_value not in self.options2:
            self.options2.insert(0, previus_value)
        if new_value in self.options2:
            self.options2.remove(new_value)
        if new_value == self.var2.get():
            self.var2.set(self.options2[0])
        self.option_menu_second.updater(options=self.options2)

class PathAdressGroup(tk.Frame):
    def __init__(self, parent, window, bg_color, text_color, line_color, *args, **kwargs):
        super().__init__(
            parent,
            background=bg_color,
        )
        self.desc_label = tk.Label(
            self,
            background=bg_color,
            fg=text_color,
            text="Sonuçların kaydedilmesini istediğiniz klasörün yolunu giriniz:",
            font=("JetBrainsMonoRoman Regular", 12),
        )
        self.inner_path_frame = tk.Frame(
            self,
            background=bg_color,
            height=30
        )
        self.save_path = tk.Text(
            self.inner_path_frame,
            height=1,
            font=("JetBrainsMonoRoman Regular", 12),
            fg='#747474',
            background=line_color,
            border=0,
            pady=4,
            insertbackground='#c0c0c0'
        )
        self.browse_button = MyButton(
            self.inner_path_frame,
            text='Browse',
            background=line_color,
            text_color='white',
            width=100,
            height=25,
            round=0,
            align_text="center",
            font=("Helvatica", 9)
        )

        self.browse_button.bind("<Button-1>", lambda e: self.browse_click(e, '#8AB4F8', 'black', self.save_path))
        self.browse_button.bind("<ButtonRelease-1>", lambda e: self.browse_color_change(e, '#727478', 'white'))
        self.browse_button.bind("<Enter>", lambda e: self.browse_color_change(e, '#727478', text_color))
        self.browse_button.bind("<Leave>", lambda e: self.browse_color_change(e, line_color, 'white'))

        placeholder = "Example: C:/Users/Username/Desktop/sonuc"
        self.save_path.insert("1.0", placeholder)
        window.unbind("<Button-1>")
        self.save_path.bind("<Button-1>", lambda e: on_focus_in(e, self.save_path, placeholder, text_color))
        self.save_path.bind("<FocusOut>", lambda e: on_focus_out(e, self.save_path, placeholder, text_color))
        window.bind("<Button-1>", lambda e: on_click_outside(e, self.save_path, placeholder, text_color))

        self.desc_label.grid(column=0, row=0, sticky='w')
        self.inner_path_frame.grid(column=0, row=0, sticky='ew')
        self.inner_path_frame.pack_propagate(False)
        self.browse_button.pack(side=tk.RIGHT, padx=10)
        self.save_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.window = window
    def browse_click(self, event, c, t, text_item):
        self.browse_color_change(event,c,t)
        browse_directory(text_item, w=self.window)

    def browse_color_change(self,e,c,t):
        self.browse_button.config(background=c, text_color=t)
