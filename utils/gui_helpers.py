import os
import platform
import subprocess
import ctypes as ct
import tkinter as tk
from tkinter import messagebox


def open_folder_in_explorer(folder_path):
    absolute_path = os.path.abspath(folder_path)
    if os.name == "nt":  # Windows
        subprocess.run(["explorer", absolute_path])
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", absolute_path])
    else:  # Linux
        subprocess.run(["xdg-open", absolute_path])


def dark_title_bar(window):
    if os.name != "nt":
        return
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))


def Error_box(Error):
    messagebox.showerror("Error", f"Error: {Error}")


def text_print(text_widget: tk.Text, text: str, color="#E3E3E3"):
    text = text + "\n"
    text_widget.config(state=tk.NORMAL, fg=color)
    text_widget.insert(tk.END, text)
    text_widget.see(tk.END)
    text_widget.config(state=tk.DISABLED)


def hata_print(text_widget: tk.Text, text: str):
    text = text + "\n"
    text_widget.config(state=tk.NORMAL, fg="red")
    text_widget.insert(tk.END, text)
    text_widget.see(tk.END)
    text_widget.config(state=tk.DISABLED)


def calculate_scale(window, base_width, base_height):
    new_width = window.winfo_width()
    new_height = window.winfo_height()

    # Sıfıra bölünme hatasını engelle
    if base_width == 0 or base_height == 0:
        return 1.0

    scale = (new_width * new_height) / (base_width * base_height)
    scale = round(scale, 1)

    # Sınırlandırmalar
    if scale <= 1:
        scale = 1.0
    elif scale >= 1.60:
        scale = 1.60

    return scale


def silici(canvas, canvas2, window):
    items = canvas2.find_all()

    # Her bir öğeyi yok eder (Sadece Canvas üzerindeki şekiller)
    for item in items:
        canvas2.delete(item)

    for widget in canvas2.winfo_children():
        widget.destroy()

    except_list = [canvas, canvas2]
    for widget in window.winfo_children():
        if widget not in except_list:
            widget.destroy()


def width_f(widtha, canvas2):
    deneme_label = tk.Label(canvas2, text="0", bg="black", border=0)
    deneme_label.place(x=50000, y=0)
    deneme_label.update()
    a = deneme_label.winfo_width()
    deneme_label.destroy()
    widtha = round(widtha / a)
    return widtha


def smooth_scroll(delta, canvas, count, window):
    """Mouse wheel scroll hareketini smooth hale getirir."""
    if delta > 0:
        canvas.yview_scroll(-1, "units")  # Yukarı kaydırma
    else:
        canvas.yview_scroll(1, "units")  # Aşağı kaydırma
    count -= 1
    if count >= 0:
        window.after(
            10, lambda: smooth_scroll(delta, canvas, count)
        )  # 10 ms sonra tekrar çağır


def color_change(old_color, new_color, window):
    global color
    widgets = window.winfo_children()
    for widget in widgets:
        if widget.cget("background") == old_color:
            widget.config(bg=new_color)
    color = new_color
