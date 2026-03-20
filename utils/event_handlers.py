import tkinter as tk


def on_focus_in(event, text_widget, placeholder, active_text_color="#E3E3E3"):
    if text_widget.get("1.0", tk.END).strip("\n") == placeholder:
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.config(fg=active_text_color)
    else:
        text_widget.config(state=tk.NORMAL)


def on_focus_out(event, text_widget, placeholder, inactive_color="#747474"):
    if not text_widget.get("1.0", tk.END).strip("\n"):
        text_widget.insert("1.0", placeholder)
        text_widget.config(fg=inactive_color)
        text_widget.config(state=tk.DISABLED)
    else:
        text_widget.config(state=tk.DISABLED)


def on_click_outside(
    event, text_widgets, placeholder_default, inactive_color="#747474"
):
    # Tekil objeyi standart bir liste yapısına çevirerek karmaşık if/else bloklarını ortadan kaldırdık
    if not isinstance(text_widgets, list):
        text_widgets = [(text_widgets, placeholder_default)]

    for text_widget_data in text_widgets:
        try:
            text_widget = text_widget_data[0]
            ph = text_widget_data[1]
            widget = event.widget

            if widget != text_widget and widget.winfo_containing(
                event.x_root, event.y_root
            ):
                on_focus_out(None, text_widget, ph, inactive_color)
        except (AttributeError, tk.TclError):
            # Yalnızca beklenen GUI nesnesi hataları görmezden gelinir
            pass


def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def on_text_enter(event, canvas):
    canvas.unbind_all("<MouseWheel>")


def on_text_leave(event, canvas):
    canvas.bind_all("<MouseWheel>", lambda e: on_mouse_wheel(e, canvas))


def on_button_click(option_menu):
    option_menu.toggle()


def button_hover(
    event, button, dictionary, button_5, program_icon_hover, home_icon_hover
):
    if dictionary[button] == 0 and button != button_5:
        button.config(background="#3C4043", image=program_icon_hover)
    elif dictionary[button] == 0 and button == button_5:
        button.config(background="#3C4043", image=home_icon_hover)


def button_leave(
    event,
    button,
    dictionary,
    color,
    button_5,
    program_icon_notselected,
    home_icon_notselected,
):
    if dictionary[button] == 0 and button != button_5:
        button.config(background=color, image=program_icon_notselected)
    elif dictionary[button] == 0 and button == button_5:
        button.config(background=color, image=home_icon_notselected)


def show_menu(
    event, options, var, button, window, color, canvas2_text_color, line_color
):
    # Menü oluşturma
    menu = tk.Menu(
        window,
        borderwidth=0,
        activeborderwidth=0,
        relief="flat",
        tearoff=2,
        background=color,
        fg=canvas2_text_color,
        activebackground=line_color,
        cursor="hand2",
    )

    for option in options:
        menu.add_command(label=option, command=lambda opt=option: var.set(opt))
    menu.post(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height())
