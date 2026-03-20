import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


def browse_directory(text_widget, parent_window, text_color="#E3E3E3"):
    folder_selected = filedialog.askdirectory(parent=parent_window)
    text_widget.config(state=tk.NORMAL)
    if folder_selected:
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, folder_selected)
    if text_widget.get("1.0", tk.END) != "Example: C:/Users/Username/Desktop/sonuc\n":
        text_widget.config(fg=text_color)


def browse_excel(text_widget, parent_window, text_color="#E3E3E3"):
    file_path = filedialog.askopenfilename(
        parent=parent_window,
        title="Bir Excel dosyası seçin",
        filetypes=[("Excel Files", "*.xlsx *.xls")],
    )
    text_widget.config(state=tk.NORMAL)
    if file_path:
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, file_path)
    if text_widget.get("1.0", tk.END) != "Example: C:/Users/Username/Desktop/sonuc\n":
        text_widget.config(fg=text_color)


def placeholder_finder(name: str):
    try:
        with open(f"Settings/Placeholder/{name}.txt", "r", encoding="utf-8") as file:
            placeholder = file.readlines()
        return placeholder
    except FileNotFoundError:
        os.makedirs("Settings/Placeholder", exist_ok=True)
        with open(f"Settings/Placeholder/{name}.txt", "w", encoding="utf-8") as file:
            pass
        return []


def placeholder_saver(name: str, output_text: tk.Text):
    new_path = output_text.get(1.0, tk.END).strip("\n")
    os.makedirs("Settings/Placeholder", exist_ok=True)
    name_var = ""
    try:
        with open(f"Settings/Placeholder/{name}.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            if len(lines) > 1:
                name_var = lines[1].strip("\n")
    except FileNotFoundError:
        pass

    new_text = f"{new_path}\n{name_var}"
    with open(f"Settings/Placeholder/{name}.txt", "w", encoding="utf-8") as file:
        file.write(new_text)


def save_location_saver(name: str, save_text: tk.Text):
    new_name = save_text.get(1.0, tk.END).strip("\n")
    os.makedirs("Settings/Placeholder", exist_ok=True)
    lines = []
    try:
        with open(f"Settings/Placeholder/{name}.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        pass

    if len(lines) > 0:
        lines = lines[:-1]
    lines.append(new_name)

    with open(f"Settings/Placeholder/{name}.txt", "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line.strip("\n") + "\n")


def path_text_function(
    name, path_text, placeholder, save_text: tk.Text = None, text_color="#E3E3E3"
):
    memorytext = placeholder_finder(name)
    memorypath = memorytext[0].strip("\n") if memorytext else ""

    if memorypath and memorypath != placeholder:
        path_text.insert("1.0", memorypath)
        path_text.config(foreground=text_color)
    else:
        path_text.insert("1.0", placeholder)
        path_text.config(foreground="#747474")

    if save_text is not None and len(memorytext) > 1:
        memorysavename = memorytext[1].strip("\n")
        save_text.insert("1.0", memorysavename)


def relative_to_assets(path: str) -> Path:
    OUTPUT_PATH = Path(__file__).resolve().parent.parent
    ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"
    return ASSETS_PATH / path


def write_settings(isim, settings_var):
    with open(isim, "w", encoding="utf-8") as file:
        file.write(settings_var)
