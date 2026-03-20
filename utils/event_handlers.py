import tkinter as tk

def on_focus_in(event, text_widget, placeholder, active_text_color='#E3E3E3'):
    if text_widget.get("1.0", tk.END).strip('\n') == placeholder:
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.config(fg=active_text_color)
    else:
        text_widget.config(state=tk.NORMAL)

def on_focus_out(event, text_widget, placeholder, inactive_color="#747474"):
    if not text_widget.get("1.0", tk.END).strip('\n'):
        text_widget.insert("1.0", placeholder)
        text_widget.config(fg=inactive_color)
        text_widget.config(state=tk.DISABLED)
    else:
        text_widget.config(state=tk.DISABLED)

def on_click_outside(event, text_widgets, placeholder_default, inactive_color="#747474"):
    # Tekil objeyi standart bir liste yapısına çevirerek karmaşık if/else bloklarını ortadan kaldırdık
    if not isinstance(text_widgets, list):
        text_widgets = [(text_widgets, placeholder_default)]
        
    for text_widget_data in text_widgets:
        try:
            text_widget = text_widget_data[0]
            ph = text_widget_data[1]
            widget = event.widget
            
            if widget != text_widget and widget.winfo_containing(event.x_root, event.y_root):
                on_focus_out(None, text_widget, ph, inactive_color)
        except (AttributeError, tk.TclError):
            # Yalnızca beklenen GUI nesnesi hataları görmezden gelinir
            pass