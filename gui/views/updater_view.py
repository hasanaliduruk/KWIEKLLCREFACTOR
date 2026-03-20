import tkinter as tk
from tkinter import (
    Frame,
    Label,
    ttk,
    Toplevel,
    Text,
    WORD,
    LEFT,
    BOTH,
    RIGHT,
    BOTTOM,
    X,
    DISABLED,
    END,
    messagebox,
)
from threading import Thread
import os
import tempfile

from gui.components.custom_buttons import MyButton
from core.updater_service import (
    check_internet,
    get_latest_release,
    download_update_file,
    prepare_and_run_batch,
)


def render_updater_view(
    canvas2, color, window, line_color, canvas2_text_color, CURRENT_VERSION
):

    # --- UI BİLEŞENLERİ (GÖRÜNÜM) ---
    checkforupdates_label = Label(
        canvas2,
        text="Güncellemeleri kontrol etmek için Check For Updates butonuna tıklayın:",
        font=("JetBrainsMonoRoman Regular", 12),
        bg=color,
        fg=canvas2_text_color,
    )

    checkforupdates = MyButton(
        canvas2,
        round=5,
        width=150,
        height=45,
        text="Check For Updates",
        background=line_color,
        text_color="white",
        align_text="center",
    )

    doyouwanna_frame = Frame(canvas2, bg=color)
    doyouwanna_label = Label(
        doyouwanna_frame,
        bg=color,
        fg=canvas2_text_color,
        text="Yeni bir güncelleme bulundu! Yüklemek istiyor musun?",
        font=("JetBrainsMonoRoman Regular", 12),
    )

    release_notes_btn = MyButton(
        doyouwanna_frame,
        round=5,
        width=125,
        height=30,
        text="Release Notes",
        background=line_color,
        text_color="white",
        align_text="center",
    )

    yes_button = MyButton(
        doyouwanna_frame,
        round=5,
        width=75,
        height=30,
        text="Yükle",
        background=line_color,
        text_color="white",
        align_text="center",
    )

    # İndirme Çubuğu (Varsayılan olarak gizli)
    progress_label = Label(
        window, bg=color, fg=canvas2_text_color, text="İndiriliyor..."
    )
    progress_bar = ttk.Progressbar(window, orient="horizontal", mode="determinate")

    # --- BUTON EFEKTLERİ ---
    def color_change(e, c, t, btn):
        btn.config(background=c, text_color=t)

    for btn in [yes_button, release_notes_btn, checkforupdates]:
        btn.bind(
            "<ButtonRelease-1>", lambda e, b=btn: color_change(e, "#727478", "white", b)
        )
        btn.bind(
            "<Enter>",
            lambda e, b=btn: color_change(e, "#727478", canvas2_text_color, b),
        )
        btn.bind("<Leave>", lambda e, b=btn: color_change(e, line_color, "white", b))

    # --- YERLEŞİM (LAYOUT) ---
    doyouwanna_frame.grid_columnconfigure(0, weight=1)
    doyouwanna_label.grid(column=0, row=0, sticky="w", pady=(0, 10))
    release_notes_btn.grid(column=0, row=1, sticky="e", padx=(0, 5))
    yes_button.grid(column=1, row=1, sticky="e")

    canvas2.grid_columnconfigure(0, weight=1)
    checkforupdates_label.grid(column=0, row=0, sticky="w")
    canvas2.update_idletasks()
    checkforupdates.grid(
        column=0,
        row=1,
        padx=(checkforupdates_label.winfo_width() - 150, 0),
        pady=(10, 0),
        sticky="w",
    )

    def show_release_notes(version_tag, notes_text):
        release_window = Toplevel(window)
        release_window.geometry("500x300")
        release_window.title(f"Release Notes of {version_tag}")
        release_window.configure(bg=color)

        r_text = Text(
            release_window,
            border=0,
            wrap=WORD,
            bg=line_color,
            fg="#c0c0c0",
            font=("JetBrainsMonoRoman Regular", 10),
            insertbackground="#c0c0c0",
        )
        r_text.insert(END, notes_text)
        r_text.see(END)
        r_text.config(state=DISABLED)
        r_text.pack(side=LEFT, fill=BOTH, expand=True, anchor="nw")

    def start_download_process(asset_url):
        progress_bar.pack(side=BOTTOM, fill=X)
        progress_label.pack(side=BOTTOM, anchor="w")
        yes_button.unbind("<Button-1>")  # Çift tıklamayı önle

        def update_progress(downloaded, total):
            percentage = (downloaded / total) * 100 if total > 0 else 0
            window.after(
                0, lambda: progress_bar.configure(value=downloaded, maximum=total)
            )
            window.after(
                0,
                lambda: progress_label.config(
                    text=f"%{int(percentage)} İndiriliyor..."
                ),
            )

        def run_download():
            temp_path = os.path.join(tempfile.gettempdir(), "KWIEKLLC_update.exe")
            success = download_update_file(
                asset_url, temp_path, progress_callback=update_progress
            )

            if success:
                window.after(
                    0,
                    lambda: progress_label.config(
                        text="İndirme tamamlandı! Kuruluyor, lütfen bekleyin..."
                    ),
                )
                window.after(1000, lambda: prepare_and_run_batch(temp_path))
                window.after(3000, lambda: os._exit(0))  # Uygulamayı güvenle kapat
            else:
                window.after(
                    0,
                    lambda: messagebox.showerror(
                        "Hata", "Güncelleme indirilirken bir sorun oluştu."
                    ),
                )
                window.after(0, lambda: progress_bar.pack_forget())
                window.after(0, lambda: progress_label.pack_forget())

        Thread(target=run_download, daemon=True).start()

    def check_for_updates_logic():
        """İnterneti ve API'yi kontrol eder, sonuca göre arayüzü günceller."""
        window.after(
            0,
            lambda: checkforupdates_label.config(
                text="Güncellemeler kontrol ediliyor, lütfen bekleyin..."
            ),
        )

        if not check_internet():
            window.after(
                0,
                lambda: checkforupdates_label.config(
                    text="Hata: İnternet bağlantısı kurulamadı."
                ),
            )
            window.after(
                0,
                lambda: messagebox.showwarning(
                    "Bağlantı Hatası",
                    "İnternet bağlantınızı kontrol edip tekrar deneyin.",
                ),
            )
            return

        release_data = get_latest_release()

        if not release_data:
            window.after(
                0,
                lambda: checkforupdates_label.config(
                    text="Hata: Güncelleme sunucusuna ulaşılamadı."
                ),
            )
            return

        latest_version = release_data.get("tag_name", "v0.0.0")

        if latest_version > CURRENT_VERSION:
            release_notes_text = release_data.get("body", "No release notes provided.")
            asset_url = (
                release_data["assets"][0]["browser_download_url"]
                if release_data.get("assets")
                else None
            )

            if not asset_url:
                window.after(
                    0,
                    lambda: messagebox.showerror(
                        "Hata", "Yeni versiyon var ancak indirme linki bulunamadı."
                    ),
                )
                return

            window.after(
                0,
                lambda: checkforupdates_label.config(
                    text=f"Mevcut Versiyon: {CURRENT_VERSION} | Bulunan Versiyon: {latest_version}"
                ),
            )

            # Butonlara işlevlerini bağla
            release_notes_btn.bind(
                "<Button-1>",
                lambda e: show_release_notes(latest_version, release_notes_text),
            )
            yes_button.bind("<Button-1>", lambda e: start_download_process(asset_url))

            # Çerçeveyi görünür yap
            window.after(
                0,
                lambda: doyouwanna_frame.grid(
                    column=0, row=2, sticky="w", pady=(20, 0)
                ),
            )
        else:
            window.after(
                0,
                lambda: checkforupdates_label.config(
                    text="Uygulama en güncel sürümde!"
                ),
            )
            window.after(0, lambda: doyouwanna_frame.grid_forget())

    # Check For Updates butonuna basıldığında Thread'i tetikle
    checkforupdates.bind(
        "<Button-1>",
        lambda e: Thread(target=check_for_updates_logic, daemon=True).start(),
    )
