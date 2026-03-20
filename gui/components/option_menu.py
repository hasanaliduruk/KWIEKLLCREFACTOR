import tkinter as tk

class CustomOptionMenu(tk.Frame):
    def __init__(self, window, parent, options, parent_button:tk.Button,var,cursor='hand2', command=None, outline_color='black', outline_width=1, background_color='white', foreground_color='black', on_enter_color='black', on_enter_fg='white'):
        super().__init__(window, background=background_color, highlightthickness=outline_width, highlightcolor=outline_color, highlightbackground=outline_color)
        global previus_value
        previus_value = var
        self.command = command
        self.options = options
        self.visible = False
        self.buttons = []
        self.parent_button = parent_button
        self.window = window
        self.var = var
        self.on_enter_color = on_enter_color
        self.on_enter_fg = on_enter_fg
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.background_color = background_color
        self.foreground_color = foreground_color
        for option in options:
            button = tk.Label(self, text=option, relief="solid", padx=10, pady=5, border=0, bg=background_color, fg=foreground_color, cursor=cursor)
            line=tk.Frame(self, height=outline_width, bg=outline_color)
            button.bind("<Button-1>", self.on_option_click)
            self.buttons.append(button)
            button.pack(fill="x")
            button.bind("<Enter>", lambda e: self.on_enter(e, on_enter_color, on_enter_fg))
            button.bind("<Leave>", lambda e: self.on_enter(e, background_color, foreground_color))
            if option != options[-1]:
                line.pack(fill="x")
    def updater(self, options):
        items = self.winfo_children()
        for item in items:
            item.destroy()
        for option in options:
            button = tk.Label(self, text=option, relief="solid", padx=10, pady=5, border=0, bg=self.background_color, fg=self.foreground_color)
            line=tk.Frame(self, height=self.outline_width, bg=self.outline_color)
            button.bind("<Button-1>", self.on_option_click)
            self.buttons.append(button)
            button.pack(fill="x")
            button.bind("<Enter>", lambda e: self.on_enter(e, self.on_enter_color, self.on_enter_fg))
            button.bind("<Leave>", lambda e: self.on_enter(e, self.background_color, self.foreground_color))
            if option != options[-1]:
                line.pack(fill="x")
    def on_enter(self, event, color, fg):
        event.widget.config(bg=color, fg=fg)
    def toggle(self):
        if self.visible:
            self.place_forget()
            self.window.unbind("<Button-1>")
        else:
            x = self.window.winfo_rootx()
            y = self.window.winfo_rooty()
            self.place(x=self.parent_button.winfo_rootx()-x, y=self.parent_button.winfo_rooty()+self.parent_button.winfo_height()-y, width=self.parent_button.winfo_width())
            self.window.bind("<Button-1>", self.on_click_outside)
        self.visible = not self.visible

    def on_option_click(self, event):
        option = event.widget.cget("text")
        self.on_option_select(option, self.var)
        self.toggle()
    def on_option_select(self, option, selected_option):
        #print(f"Seçilen seçenek: {option}")
        global previus_value
        previus_value = selected_option.get()
        selected_option.set(option)
    def on_click_outside(self, event):
        if self.visible:
            widget = event.widget
            if widget != self.parent_button and widget.winfo_containing(event.x_root, event.y_root):
                self.toggle()
        self.window.unbind("<Button-1>")