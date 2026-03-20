import os
import platform
import subprocess
import ctypes as ct
import tkinter as tk
from tkinter import messagebox

def open_folder_in_explorer(folder_path):
    absolute_path = os.path.abspath(folder_path)
    if os.name == 'nt': # Windows
        subprocess.run(['explorer', absolute_path])
    elif platform.system() == "Darwin": # macOS
        subprocess.run(['open', absolute_path])
    else: # Linux
        subprocess.run(['xdg-open', absolute_path])

def dark_title_bar(window):
    if os.name != 'nt':
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
    messagebox.showerror('Error', f'Error: {Error}')

def text_print(text_widget: tk.Text, text: str, color='#E3E3E3'):
    text = text + '\n'
    text_widget.config(state=tk.NORMAL, fg=color)
    text_widget.insert(tk.END, text)
    text_widget.see(tk.END)
    text_widget.config(state=tk.DISABLED)

def hata_print(text_widget: tk.Text, text: str):
    text = text + '\n'
    text_widget.config(state=tk.NORMAL, fg='red')
    text_widget.insert(tk.END, text)
    text_widget.see(tk.END)
    text_widget.config(state=tk.DISABLED)