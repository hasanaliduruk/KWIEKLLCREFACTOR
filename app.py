"""
app.py — Desktop entry point for the webview version of the app.

This replaces every tkinter window/view with a single native window that
displays gui_web/index.html. All the original business logic in core/ is
untouched — this file just wires HTML/JS buttons to those same functions.

Run with:  python app.py
"""

import os
import sys
import json
import socket
import tempfile
import subprocess
import traceback
from threading import Thread
import time

import requests  # pip install requests — used by the auto-updater
import webview  # pip install pywebview
from webview.dom import DOMEventHandler
import keyring  # pip install keyring — stores the Expiration tool's password
                 # in the OS credential vault (Windows Credential Manager,
                 # macOS Keychain, etc.) instead of a plaintext settings file.

from core.converter import process_conversion
from core.cost_updater import process_costupdater
from core.restock_processor import process_restock_logic
from core.tsv_converter import convert_tsv_to_excel, compare_and_write
from core.invoice_processor import process_invoice
from core.order_creator import process_order_create
from core.shipment_creator import process_shipment_creation
from core.future_price_updater import process_future_price
from core.invoice_finder import process_invoice_finder, process_invoice_finder_upc
from core.expiration_processor import process_expiration

# ---------------------------------------------------------------------------
# Version / auto-updater
# ---------------------------------------------------------------------------

CURRENT_VERSION = "v1.2.4"
GITHUB_API_URL = "https://api.github.com/repos/hasali2603/KWIEKLLC/releases/latest"


def get_asset_path(relative_name):
    """Resolve an asset path that works both in dev and in PyInstaller _internal."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = APP_DIR
    return os.path.join(base, "assets", relative_name)


# ---------------------------------------------------------------------------
# Paths / settings bootstrap
# ---------------------------------------------------------------------------

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# core/restock_processor.py reads "Settings/restock_settings.txt" as a
# path relative to the current working directory (a holdover from the
# original tkinter app, which was always launched from the project root).
# We pin the working directory here so that still works no matter how
# this script is launched (double-click, shortcut, different shell cwd).
os.chdir(APP_DIR)

SETTINGS_DIR = os.path.join(APP_DIR, "Settings")
os.makedirs(SETTINGS_DIR, exist_ok=True)

DEFAULT_SETTINGS = {
    "costupdater_settings.txt": (
        "cost = cost\n"
        "sku = sku\n"
        "additional cost = additional_cost\n"
        "business pricing = business_pricing\n"
        "bp strategy = bp_strategy\n"
        "qd strategy = qd_strategy\n"
        "====================================\n"
        "BX: 0.3\nCANDY: 0.3\nCOS: 0.3\nCS: 0.3\nCSC: 0.3\nDL: 0.3\nFC: 0.3\n"
        "FD: 0.3\nFL: 0.75\nFOUR: 0.3\nFR: 0.3\nGEMCO: 0.3\nIL: 0.75\nJC: 0.3\n"
        "KH: 0.3\nLR: 0.3\nMD: 0.75\nMONIN PUMP SL: 0.3\nNC: 0.3\nNF: 0.3\n"
        "NJ: 0.3\nNK: 0.3\nNT: 0.3\nSN: 0.3\nUC: 0.3\nUD: 0.3\nUN: 0.3\n"
        "UPC: 0.3\nWB: 0.3\nWEBS: 0.3\n"
    ),
    "costupdater2_settings.txt": (
        "cost = cost\n"
        "sku = sku\n"
        "additional cost = additional_cost\n"
        "business pricing = business_pricing\n"
        "bp strategy = bp_strategy\n"
        "qd strategy = qd_strategy\n"
        "pkg volume = pkg_volume\n"
        "pkg weight = pkg_weight\n"
        "====================================\n"
        "DC_NAME: ADDITIONAL_COST EQUATION_NUMBER DEPOSIT_COST\n"
        "BX: 0 2 0.70\nCANDY: 0 2 0.70\nCOS: 0 2 0.70\nCS: 0 2 0.70\n"
        "CSC: 0 2 0.70\nDL: 0 2 0.70\nFC: 0 2 0.70\nFD: 0 2 0.70\nFL: 0 1 0.70\n"
        "FOUR: 0 2 0.70\nFR: 0 2 0.70\nGEMCO: 0 2 0.70\nIL: 0 1 0.70\n"
        "JC: 0 2 0.70\nKH: 0 2 0.70\nLR: 0 2 0.70\nMD: 0 1 0.70\n"
        "MONIN PUMP SL: 0 2 0.70\nNC: 0 2 0.70\nNF: 0 2 0.70\nNJ: 0 2 0.70\n"
        "NK: 0 2 0.70\nNT: 0 2 0.70\nSN: 0 2 0.70\nUC: 0 2 0.70\nUD: 0 2 0.70\n"
        "UN: 0 2 0.70\nUPC: 0 2 0.70\nWB: 0 2 0.70\nWEBS: 0 2 0.70\nTD: 0 2 0.70\n"
        "IN: 0 1 0.70\nBL: 0 2 0.70\nYT: 0 1 0.70\nBZ: 0 1 0.70\nMI: 0 2 0.70"
    ),
    "restock_settings.txt": (
        "upc = UPC, upc, Upc, UPC #\n"
        "brand = BRAND, Brand, brand\n"
        "price = NET_AMOUNT, Price, price\n"
        "case = CASEPACK, Size, Case, case, size\n"
        "Quantity on hand = Qty on Hand, Quantity Available\n"
        "pk = PK\n"
        "======================================\n"
        "41 cost: 0.78\n41 standart: 0.78\n45 cost: 0.78\n45 standart: 0.78\n"
        "19 cost: 0.78\n19 standart: 0.78\n27 cost: 1.10\n27 standart: 1.10\n"
        "18 cost: 1.10\n18 standart: 1.10\n01 cost: 1.10\n01 standart: 1.10\n"
        "NF: 0.78"
    ),
    "invoice_settings.txt": (
        "remove = Status, QuantityNotShipped, InvalidReason\n"
        "shipquantity = ShipQuantity\n"
        "date = InvoiceDate"
    ),
    "invoicefinder_yonergeler.txt": (
        "Invoice Finder Programı Yönergeleri:\n\n"
        "1. Ekranınızda gözükmekte olan ilk boşluğa orada da belirtildiği üzere "
        "uygulamanın bulmuş olduğu invoice dosyalarının ve en son uygulamanın "
        "oluşturacağı excel dosyasının kaydedileceği dosya yolunu gerek elinizle "
        "yazarak gerek Browse butonunu kullanarak uygulamaya belirtiniz.\n\n"
        "2. İkinci boşluğa ise bilgisayarınızda bulunan bütün invoice pdf "
        "dosyalarını içeren klasörün yolunu 1. yönergede belirtildiği şekilde "
        "giriniz.\n\n"
        "3. Üçüncü boşluğa ise içeriğinde bütün Upc değerleri ve o değerlere "
        "karşılık gelen invoice numaralarını içeren ALL INVOICES excelini "
        "önceki maddelerde belirtildiği şekilde giriniz.\n\n"
        "4. Dördüncü boşluğa ise uygulamanın hangi tarihten önceki invoiceleri "
        "tarayacağını giriniz.\n\n"
        "5. İlk 3 Dosya yolunu \"Kaydet\" butonu arayıcılığıyla daha sonraki "
        "işlemlerinizde de kullanmak amacıyla kaydedebilirsiniz.\n\n"
        "6. Bütün bu dosya yolu girme yerlerinin altında bir adet sürükle ve "
        "bırak yöntemi ile dosya algılayan alan göreceksiniz. O alana Amazonun "
        "sitesinden kopyalayarak aldığınız verileri bir excele metin olarak "
        "yapıştırıp oluşturduğunuz excel dosyasını belirtilen alana fare "
        "imlecinizle tutup bırakınız.\n\n"
        "7. İşlemi başlatmak için \"Başlat\" butonunuza basmanız yeterlidir.\n\n"
        "-------------SÜTUN İSİMLERİ---------------\n\n"
        "ALL INVOICES EXCEL DOSYASI İÇİN:\n\n"
        "ship quantity = ShipQuantity\n"
        "item number = ShipItem\n"
        "UPC = Upc\n"
        "Invoice Number = InvoiceNumber\n"
        "Date = Date"
    ),
    "ordercreate_settings.txt": (
        "RESTOCK:\n"
        "upc = Upc\n"
        "pcs = PCS\n"
        "suplier = suplier\n"
        "notes = Notes\n"
        "=====================================================\n"
        "ORDER FORM:\n"
        "upc = UPC\n"
        "pcs = PCS(TOTAL)\n"
        "suplier = supplier"
    ),
    "shipment_settings.txt": (
        "RESTOCK:\n"
        "upc = Upc\n"
        "pcs = PCS\n"
        "asin = ASIN\n"
        "pk = PK\n"
        "price = Price\n"
        "suplier = suplier\n"
        "=====================================================\n"
        "ORDER FORM:\n"
        "upc = UPC\n"
        "pcs = PCS\n"
        "asin = ASIN 1, ASIN 2, ASIN 3, ASIN 4\n"
        "SKU = ASIN1_SKU, ASIN2_SKU, ASIN3_SKU, ASIN4_SKU\n"
        "pk = PK\n"
        "price = price\n"
        "suplier = suplier\n"
        "=====================================================\n"
        "INVOICE:\n"
        "shipquantity = ShipQuantity\n"
        "upc = Upc\n"
        "price = NetEach2\n"
        "packsize = PackSize\n"
        "brand = Brand\n"
        "description = Description"
    ),
}


def ensure_default_settings():
    """Write default settings files on first run, exactly like the old app did."""
    for filename, content in DEFAULT_SETTINGS.items():
        path = os.path.join(SETTINGS_DIR, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    # Order Creator reads a fixed template file rather than letting the user
    # pick one each run (same as the original app). Just make sure the
    # folder exists so the "open template folder" button has somewhere to
    # go on a brand-new install — the actual Template.xlsx still needs to
    # be placed there by hand (or copied over from the old app's Settings
    # folder) since we have no safe default to generate automatically.
    os.makedirs(os.path.join(SETTINGS_DIR, "Template"), exist_ok=True)


def read_settings_file(filename: str) -> str:
    path = os.path.join(SETTINGS_DIR, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_settings_file(filename: str, content: str):
    path = os.path.join(SETTINGS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Small persisted "memory" for last-used paths (replaces Settings/Placeholder)
# ---------------------------------------------------------------------------

MEMORY_PATH = os.path.join(SETTINGS_DIR, "last_paths.json")


def load_memory() -> dict:
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_memory(data: dict):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


# ---------------------------------------------------------------------------
# Expiration tool credentials — username goes in the same plain memory file
# as everything else (it's not a secret), but the password goes through
# `keyring`, which stores it in the OS credential vault (Windows Credential
# Manager / macOS Keychain / Linux Secret Service) instead of a plaintext
# settings file like the original tkinter app did.
# ---------------------------------------------------------------------------

KEYRING_SERVICE = "OperationsToolkit-2DWorkflow"
KEYRING_USERNAME_KEY = "expiration_password_owner"  # see get_saved_credentials()


def get_saved_credentials():
    """Returns (username, password) — either may be "" if nothing is saved yet."""
    mem = load_memory()
    username = mem.get("expiration_username", "")
    password = ""
    if username:
        try:
            password = keyring.get_password(KEYRING_SERVICE, username) or ""
        except Exception:
            password = ""
    return username, password


def save_credentials(username: str, password: str):
    mem = load_memory()
    mem["expiration_username"] = username
    save_memory(mem)
    if username:
        keyring.set_password(KEYRING_SERVICE, username, password)


# ---------------------------------------------------------------------------
# The API object exposed to JavaScript as `window.pywebview.api`
# ---------------------------------------------------------------------------


class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    # -- generic helpers ----------------------------------------------------

    def pick_files(self, file_types=None, multiple=True):
        """Open a native 'choose file(s)' dialog. file_types e.g. ['Excel Files (*.xlsx;*.xls)']."""
        types = tuple(file_types) if file_types else ()
        result = self._window.create_file_dialog(
            webview.FileDialog.OPEN, allow_multiple=multiple, file_types=types
        )
        return list(result) if result else []

    def pick_folder(self):
        result = self._window.create_file_dialog(webview.FileDialog.OPEN)
        return result[0] if result else ""

    def open_folder(self, path):
        if not path or not os.path.exists(path):
            return
        if sys.platform == "win32":
            os.startfile(path)  # noqa
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

    def get_memory(self):
        return load_memory()

    def set_memory_value(self, key, value):
        data = load_memory()
        data[key] = value
        save_memory(data)
        return True

    def get_settings(self, filename):
        return read_settings_file(filename)

    def save_settings(self, filename, content):
        write_settings_file(filename, content)
        return True

    # -- Settings editor --------------------------------------------------------
    # Lets the webview Settings view list and reset the .txt config files.
    # The files themselves stay in the original format — no migration, no
    # conversion. Users can add arbitrary column names, DC codes, etc.

    def list_settings_files(self):
        """Return a list of {filename, content} dicts for all .txt settings files."""
        files = []
        if os.path.isdir(SETTINGS_DIR):
            for f in sorted(os.listdir(SETTINGS_DIR)):
                if f.endswith(".txt"):
                    files.append({"filename": f, "content": read_settings_file(f)})
        return files

    def reset_settings_to_default(self, filename):
        """Reset a single settings file to the bundled default. Returns True on success."""
        if filename not in DEFAULT_SETTINGS:
            return False
        write_settings_file(filename, DEFAULT_SETTINGS[filename])
        return True

    # -- progress reporting back to the page --------------------------------

    def _emit(self, channel, payload):
        """Push an event into the page. Safe to call from a worker thread."""
        if not self._window:
            return
        js = f"window.dispatchEvent(new CustomEvent('{channel}', {{detail: {json.dumps(payload)}}}))"
        try:
            self._window.evaluate_js(js)
        except Exception:
            pass

    # -- drag & drop ----------------------------------------------------------
    # Browsers intentionally hide real filesystem paths from plain JS drag-drop
    # events. pywebview restores this via window.dom: binding a 'drop' handler
    # directly on each .dropzone element (done once in main(), after the page
    # loads) gives us both the dropped files' real paths AND, because we bind
    # per-element with the zone's id captured in the closure, which dropzone
    # received them — no need to inspect event.target at all.

    def bind_dropzones(self):
        """Called once after the window is shown. Attaches a native drop
        handler to every element with class .dropzone currently in the DOM."""
        try:
            zones = self._window.dom.get_elements(".dropzone")
        except Exception:
            return
        for zone in zones:
            zone_id = zone.id
            zone.events.dragover += DOMEventHandler(lambda e: None, True, True)
            zone.events.drop += DOMEventHandler(
                lambda e, zid=zone_id: self._handle_drop(zid, e), True, True
            )

    def _handle_drop(self, zone_id, event):
        try:
            files = (event.get("dataTransfer") or {}).get("files", [])
            paths = [f.get("pywebviewFullPath") for f in files if f.get("pywebviewFullPath")]
            if paths:
                self._emit("files-dropped", {"zoneId": zone_id, "paths": paths})
        except Exception:
            pass

    # -- Converter ------------------------------------------------------------

    def run_converter(self, files, output_folder, input_type, output_type):
        def progress(msg):
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_conversion(
                    files, output_folder, input_type, output_type,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Cost Updater ---------------------------------------------------------

    def run_costupdater(self, input_file, output_folder, settings_content, version):
        def progress(msg, color="white"):
            self._emit("job-log", {"message": msg, "color": color})

        def worker():
            try:
                result = process_costupdater(
                    input_file, output_folder, settings_content,
                    version=version, progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result.get("output_path", output_folder)})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Restock --------------------------------------------------------------

    def run_restock(self, row_files, export_files, restock_files, do_export, do_restock, save_name, output_folder):
        def progress(msg, percent=None):
            self._emit("job-log", {"message": msg, "percent": percent})

        islem = {"export": 1 if do_export else 0, "restock": 1 if do_restock else 0}

        def worker():
            try:
                result = process_restock_logic(
                    path=output_folder,
                    row_files=row_files,
                    export_files=export_files,
                    restock_files=restock_files,
                    islem=islem,
                    save_name=save_name,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result.get("message", "Tamamlandı!"), "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- TSV Converter ----------------------------------------------------------
    # convert_tsv_to_excel() takes one file at a time and has no progress_callback
    # parameter at all (unlike the other core functions) — we loop over the
    # selected files here and emit our own progress between calls.

    def run_tsv(self, files, output_folder, save_name):
        def worker():
            try:
                total = len(files)
                last_path = output_folder
                tsv_settings = os.path.join(SETTINGS_DIR, "tsv_settings.txt")
                for i, f in enumerate(files, start=1):
                    self._emit("job-log", {"message": f"Converting ({i}/{total}): {os.path.basename(f)}"})
                    name = save_name if total == 1 else f"{save_name}_{i}"
                    result = convert_tsv_to_excel(f, output_folder, name, settings_path=tsv_settings)
                    last_path = result["output_path"]
                # Aggregate the converted files (original tsv_script behaviour)
                self._emit("job-log", {"message": "Dosyalar birleştiriliyor (son.xlsx)..."})
                son_path = compare_and_write(output_folder)
                self._emit("job-done", {"ok": True, "message": f"{total} file(s) converted and aggregated.", "output_path": output_folder})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Invoice Processor --------------------------------------------------------

    def run_invoice(self, files, output_folder, settings_content, delete_zeros):
        def progress(msg):
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_invoice(
                    files, output_folder, settings_content,
                    delzero=1 if delete_zeros else 0, progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Order Creator -------------------------------------------------------------
    # Template is a fixed file the company edits directly, not picked per run —
    # same as the original tkinter app (Settings/Template/Template.xlsx).

    def open_template_folder(self):
        folder = os.path.join(SETTINGS_DIR, "Template")
        os.makedirs(folder, exist_ok=True)
        self.open_folder(folder)

    def run_order_create(self, restock_files, orderform_files, output_folder, settings_content):
        def progress(msg):
            self._emit("job-log", {"message": msg})

        template_path = os.path.join(SETTINGS_DIR, "Template", "Template.xlsx")

        def worker():
            try:
                result = process_order_create(
                    restock_files=restock_files,
                    orderform_files=orderform_files,
                    template_path=template_path,
                    output_folder=output_folder,
                    settings_content=settings_content,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Shipment Creator -----------------------------------------------------------
    # Three single-file inputs (invoice, order form, restock) feeding one
    # DC-coded output workbook — same shape as Restock/Order Creator above.

    def run_shipment_creator(self, invoice_files, orderform_files, restock_files, dc_code, save_name, output_folder, settings_content):
        def progress(msg):
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_shipment_creation(
                    invoice_files=invoice_files,
                    order_form_files=orderform_files,
                    restock_files=restock_files,
                    output_folder=output_folder,
                    save_name=save_name,
                    dc_code=dc_code,
                    settings_content=settings_content,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Future Price Updater --------------------------------------------------------
    # No settings file for this one — it matches columns automatically by
    # substring (anything with "price" in the name), not via a configurable
    # mapping like the other tools.

    def run_future_price(self, restock_file, future_file, save_name, output_folder):
        def progress(msg):
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_future_price(
                    path=output_folder,
                    name=save_name,
                    restock_excel=restock_file,
                    future_excel=future_file,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Invoice Finder ----------------------------------------------------------
    # Two modes (mirrors the original switch — default/"on" is date mode):
    #   date mode: needs a dragged-in "source excel" (pasted Amazon data) plus
    #     a cutoff date, calls process_invoice_finder.
    #   UPC mode: needs a UPC list + months-back instead, no source excel,
    #     calls process_invoice_finder_upc.
    # No settings textbox for this tool — column names are fixed (see the
    # bundled invoicefinder_yonergeler.txt instructions instead).

    def get_invoice_finder_instructions(self):
        return read_settings_file("invoicefinder_yonergeler.txt")

    def run_invoice_finder_date_mode(self, source_excel, all_invoices_excel, invoice_pdf_folder, output_folder, user_input_date):
        def progress(msg):
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_invoice_finder(
                    source_excel=source_excel,
                    all_invoices_excel=all_invoices_excel,
                    invoice_pdf_folder=invoice_pdf_folder,
                    output_folder=output_folder,
                    user_input_date=user_input_date,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    def run_invoice_finder_upc_mode(self, all_invoices_excel, invoice_pdf_folder, output_folder, upcs_str, months_str):
        def progress(msg):
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_invoice_finder_upc(
                    all_invoices_excel=all_invoices_excel,
                    invoice_pdf_folder=invoice_pdf_folder,
                    output_folder=output_folder,
                    upcs_str=upcs_str,
                    months_str=months_str,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Expiration ----------------------------------------------------------------
    # Logs into 2dworkflow.com and scrapes expiration dates per shipment ID.
    # The password is stored via keyring (OS credential vault), not in a
    # plaintext settings file like the original tkinter app did — see
    # save_credentials()/get_saved_credentials() near the top of this file.

    def get_expiration_credentials(self):
        username, password = get_saved_credentials()
        return {"username": username, "password": password}

    def save_expiration_credentials(self, username, password):
        save_credentials(username, password)
        return True

    def run_expiration(self, username, password, item_ids_str, output_folder, remember):
        def progress(msg, color="white"):
            self._emit("job-log", {"message": msg, "color": color})

        if remember:
            save_credentials(username, password)

        def worker():
            try:
                result = process_expiration(
                    username=username,
                    password=password,
                    item_ids_str=item_ids_str,
                    output_path=output_folder,
                    progress_callback=progress,
                )
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})

        Thread(target=worker, daemon=True).start()
        return True

    # -- Auto-updater -----------------------------------------------------------
    # Ported from the old tkinter version's core/updater_service.py and
    # gui/views/updater_view.py. GitHub Releases-based: checks the API,
    # compares tag_name > CURRENT_VERSION, downloads the .exe asset, and
    # launches a self-replacing batch script that overwrites the running app.

    def check_internet(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except OSError:
            return False

    def get_latest_release(self):
        try:
            r = requests.get(GITHUB_API_URL, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    def download_update_file(self, url, destination, progress_callback=None):
        try:
            r = requests.get(url, stream=True, timeout=20)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(destination, "wb") as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total > 0:
                            progress_callback(downloaded, total)
            return True
        except Exception:
            return False

    def prepare_and_run_batch(self, update_exe_path):
        # The downloaded file is the Inno Setup installer (OperationsToolkit_Setup.exe).
        # Running it silently (/SILENT) overwrites the existing install in-place
        # (Inno matches the AppId and upgrades rather than double-installing).
        # The batch waits for the app to exit, launches the installer, then
        # deletes both the installer and itself.
        temp_dir = tempfile.gettempdir()
        batch_path = os.path.join(temp_dir, "run_update.bat")
        with open(batch_path, "w") as f:
            f.write(
                f"@echo off\n"
                f"timeout /t 2 > NUL\n"
                f'start "" /wait "{update_exe_path}" /SILENT /SUPPRESSMSGBOXES /NORESTART\n'
                f'del /f /q "{update_exe_path}"\n'
                f'del /f /q "%~f0" & exit\n'
            )
        subprocess.Popen(
            [batch_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

    def run_check_for_updates(self):
        """Manual check — called from the Updates view 'Check for Updates' button."""
        def worker():
            if not self.check_internet():
                self._emit("update-status", {"state": "no-internet"})
                return
            data = self.get_latest_release()
            if not data:
                self._emit("update-status", {"state": "check-failed"})
                return
            latest = data.get("tag_name", "")
            if latest > CURRENT_VERSION:
                self._emit("update-status", {
                    "state": "update-available",
                    "version": latest,
                    "notes": data.get("body", ""),
                    "assets": [{"name": a["name"], "browser_download_url": a["browser_download_url"]} for a in data.get("assets", [])],
                })
            else:
                self._emit("update-status", {"state": "up-to-date", "version": latest})
        Thread(target=worker, daemon=True).start()

    def run_silent_update_check(self):
        """Startup check — same logic but only emits a badge hint if a new version exists."""
        def worker():
            time.sleep(1)  # small delay so the window has time to render
            if not self.check_internet():
                return
            data = self.get_latest_release()
            if not data:
                return
            latest = data.get("tag_name", "")
            if latest > CURRENT_VERSION:
                self._emit("update-badge", {
                    "version": latest,
                    "notes": data.get("body", ""),
                    "assets": [{"name": a["name"], "browser_download_url": a["browser_download_url"]} for a in data.get("assets", [])],
                })
        Thread(target=worker, daemon=True).start()

    def run_download_update(self, url):
        """Download the setup installer and hand off to the self-replacing batch script."""
        def worker():
            temp_path = os.path.join(tempfile.gettempdir(), "OperationsToolkit_Setup.exe")
            def progress(dl, total):
                pct = round(dl / total * 100) if total > 0 else 0
                self._emit("update-download-progress", {"percent": pct, "downloaded": dl, "total": total})
            self._emit("update-download-progress", {"percent": 0, "message": "Starting download…"})
            ok = self.download_update_file(url, temp_path, progress_callback=progress)
            if not ok:
                self._emit("update-download-progress", {"percent": 0, "error": "Download failed."})
                return
            self._emit("update-download-progress", {"percent": 100, "message": "Installing update…"})
            self.prepare_and_run_batch(temp_path)
            # Give the batch script a moment to launch the installer,
            # then exit the app so the installer can replace it.
            Thread(target=self._delayed_exit, daemon=True).start()
        Thread(target=worker, daemon=True).start()

    def _delayed_exit(self):
        time.sleep(3)
        os._exit(0)


def _inject_icon_data_uri(window, icon_path):
    """Replace the placeholder icon elements with a base64 data URI.

    pywebview loads index.html via file://, which can't resolve relative
    paths like ../assets/icon.ico. We read the icon file once, base64-encode
    it, and inject it directly into the DOM so the favicon, loading overlay,
    and sidebar logo all render without a local HTTP server.
    """
    try:
        if not os.path.exists(icon_path):
            return
        import base64
        with open(icon_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        data_uri = f"data:image/x-icon;base64,{b64}"
        js = (
            f"(function() {{"
            f"  var uri = '{data_uri}';"
            f"  var link = document.getElementById('app-favicon');"
            f"  if (link) link.href = uri;"
            f"  var img;"
            f"  img = document.getElementById('loading-logo-img');"
            f"  if (img) img.src = uri;"
            f"  img = document.getElementById('brand-icon-img');"
            f"  if (img) img.src = uri;"
            f"}})();"
        )
        window.evaluate_js(js)
    except Exception:
        pass


def main():
    ensure_default_settings()

    api = Api()
    index_path = os.path.join(APP_DIR, "gui_web", "index.html")

    icon_path = get_asset_path("icon.ico")

    window = webview.create_window(
        "Operations Toolkit",
        index_path,
        js_api=api,
        width=1280,
        height=860,
        min_size=(960, 640),
        background_color="#15171c",
        #icon=icon_path,
    )
    api.set_window(window)

    def on_loaded():
        # All three tool views (and their dropzones) are present in the DOM
        # from the start (just hidden via CSS), so binding once here covers
        # all of them. If new views with dropzones are added dynamically in
        # the future, call api.bind_dropzones() again after inserting them.
        api.bind_dropzones()

        # Inject the app icon as a base64 data URI so the HTML <link> and
        # <img> tags work without a server (file:// can't resolve ../assets/).
        _inject_icon_data_uri(window, icon_path)

        # Silently check for updates in the background — if a newer release
        # exists on GitHub, a badge appears on the Updates nav item.
        api.run_silent_update_check()

    window.events.loaded += on_loaded

    webview.start(debug=False)


if __name__ == "__main__":
    main()