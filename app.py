"""
app.py — Desktop entry point for the webview version of the app.
"""

import os
import sys
import json
import socket
import tempfile
import subprocess
from threading import Thread, Event, Lock
from packaging import version
import time
import ctypes
import platform
import dataclasses

import requests  
import webview  
from webview.dom import DOMEventHandler
import keyring  

from core.converter import process_conversion
from core.cost_updater import process_costupdater
from core.restock_processor import process_restock_logic
from core.tsv_converter import process_tsvs_and_aggregate
from core.invoice_processor import process_invoice
from core.order_creator import process_order_create
from core.shipment_creator import process_shipment_creation
from core.future_price_updater import process_future_price
from core.invoice_finder import process_invoice_finder, process_invoice_finder_upc
from core.expiration_processor import process_expiration
from core.fba_inventory import DatabaseManager, ShipmentIDExtractor, PicklistParser, ExcelReportExporter, FIFOEngine
from core.pk_extractor import PKExtractorEngine

CURRENT_VERSION = "v1.3.6"
GITHUB_API_URL = "https://api.github.com/repos/hasanaliduruk/KWIEKLLCREFACTOR/releases/latest"

APP_DIR = os.path.dirname(os.path.abspath(__file__))

def get_asset_path(relative_name):
    """Resolve an asset path that works both in dev and in PyInstaller _internal."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = APP_DIR
    return os.path.join(base, "assets", relative_name)
    
os.chdir(APP_DIR)

if getattr(sys, "frozen", False):
    SETTINGS_BASE_DIR = os.path.dirname(sys.executable)
else:
    SETTINGS_BASE_DIR = APP_DIR

SETTINGS_DIR = os.path.join(SETTINGS_BASE_DIR, "Settings")
os.makedirs(SETTINGS_DIR, exist_ok=True)

WINDOW_STATE_FILE = os.path.join(SETTINGS_DIR, "window_state.json")

def load_window_state():
    try:
        if os.path.exists(WINDOW_STATE_FILE):
            with open(WINDOW_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    # Varsayılan ilk açılış değerleri
    return {"width": 1280, "height": 860, "x": None, "y": None, "maximized": False}

def save_window_state(window, is_maximized):
    try:
        state = {
            "width": window.width,
            "height": window.height,
            "x": window.x,
            "y": window.y,
            "maximized": is_maximized
        }
        with open(WINDOW_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass

DEFAULT_SETTINGS = {
    "costupdater_settings.json": {
        "columns": {
            "cost": ["cost"],
            "sku": ["sku"],
            "additional cost": ["additional_cost"],
            "business pricing": ["business_pricing"],
            "bp strategy": ["bp_strategy"],
            "qd strategy": ["qd_strategy"]
        },
        "warehouses": {
            "BX": 0.75, "CANDY": 0.75, "COS": 0.75, "CS": 0.75, "CSC": 0.75, 
            "DL": 0.75, "FC": 0.75, "FD": 0.75, "FL": 0.75, "FOUR": 0.75, 
            "FR": 0.75, "GEMCO": 0.75, "IL": 0.75, "JC": 0.75, "KH": 0.75, 
            "LR": 0.75, "MD": 0.75, "MONIN PUMP SL": 0.75, "NC": 0.75, 
            "NF": 0.75, "NJ": 0.75, "NK": 0.75, "NT": 0.75, "SN": 0.75, 
            "UC": 0.75, "UD": 0.75, "UN": 0.75, "UPC": 0.75, "WB": 0.75, 
            "WEBS": 0.75, "TD": 0.75, "IN": 0.75, "BL": 0.75, "YT": 0.75
        }
    },
    "costupdater2_settings.json": {
        "columns": {
            "cost": ["cost"],
            "sku": ["sku"],
            "additional cost": ["additional_cost"],
            "business pricing": ["business_pricing"],
            "bp strategy": ["bp_strategy"],
            "qd strategy": ["qd_strategy"],
            "pkg volume": ["pkg_volume"],
            "pkg weight": ["pkg_weight"]
        },
        "warehouses": {
            "BX": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "CANDY": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "COS": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "CS": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "CSC": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "DL": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "FC": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "FD": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "FL": {"v2_additional_cost": 0.0, "v2_equation": 1, "v2_warehouse_fee": 0.70},
            "FOUR": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "FR": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "GEMCO": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "IL": {"v2_additional_cost": 0.0, "v2_equation": 1, "v2_warehouse_fee": 0.70},
            "JC": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "KH": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "LR": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "MD": {"v2_additional_cost": 0.0, "v2_equation": 1, "v2_warehouse_fee": 0.70},
            "MONIN PUMP SL": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "NC": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "NF": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "NJ": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "NK": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "NT": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "SN": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "UC": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "UD": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "UN": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "UPC": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "WB": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "WEBS": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "TD": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "IN": {"v2_additional_cost": 0.0, "v2_equation": 1, "v2_warehouse_fee": 0.70},
            "BL": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "YT": {"v2_additional_cost": 0.0, "v2_equation": 1, "v2_warehouse_fee": 0.70},
            "BZ": {"v2_additional_cost": 0.0, "v2_equation": 1, "v2_warehouse_fee": 0.70},
            "MI": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "PH": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "TH": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "NW": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "BC": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "EJ": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "ST": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70},
            "PF": {"v2_additional_cost": 0.0, "v2_equation": 2, "v2_warehouse_fee": 0.70}
        }
    },
    "restock_settings.json": {
        "columns": {
            "upc": ["UPC", "upc", "Upc", "UPC #"],
            "brand": ["BRAND", "Brand", "brand"],
            "price": ["NET_AMOUNT", "Price", "price"],
            "case": ["CASEPACK", "Size", "Case", "case", "size", "Case Pack"],
            "Quantity on hand": ["Qty on Hand", "Quantity Available"],
            "pk": ["PK"]
        },
        "deposits": {
            "41 cost": 0.70,
            "41 standart": 0.70,
            "45 cost": 0.70,
            "45 standart": 0.70,
            "19 cost": 0.70,
            "19 standart": 0.70,
            "27 cost": 1.00,
            "27 standart": 1.00,
            "18 cost": 1.00,
            "18 standart": 1.00,
            "01 cost": 1.00,
            "01 standart": 1.00,
            "16 standart": 1.00,
            "NF": 0.70,
            "TD": 0.70,
            "BZ": 1.00,
            "YT": 1.00,
            "MI": 0.70,
            "PF": 0.70,
            "HN": 0.70,
            "BC": 1.00,
            "NW": 0.70,
            "TH": 0.70,
            "ST": 1.00,
            "FD": 0.70,
            "UN": 0.70,
            "PH": 0.70,
            "EJ": 0.70
        }
    },
    "ordercreate_settings.json": {
        "restock_columns": {
            "upc": ["Upc"],
            "pcs": ["PCS"],
            "suplier": ["suplier"],
            "notes": ["Notes"]
        },
        "orderform_columns": {
            "upc": ["UPC"],
            "pcs": ["PCS(TOTAL)"],
            "suplier": ["suplier"]
        }
    },
    "invoice_settings.json": {
        "columns": {
            "remove": ["Status", "QuantityNotShipped", "InvalidReason"],
            "shipquantity": ["ShipQuantity"],
            "date": ["InvoiceDate"]
        }
    },
    "shipment_settings.json": {
        "restock_columns": {
            "upc": ["Upc"],
            "pcs": ["PCS", "Pcs", "pcs"],
            "asin": ["ASIN"],
            "pk": ["PK"],
            "price": ["Price"],
            "suplier": ["suplier"]
        },
        "orderform_columns": {
            "upc": ["UPC"],
            "pcs": ["PCS"],
            "asin": ["ASIN 1", "ASIN 2", "ASIN 3", "ASIN 4"],
            "sku": ["ASIN1_SKU", "ASIN2_SKU", "ASIN3_SKU", "ASIN4_SKU"],
            "pk": ["PK"],
            "price": ["price"],
            "suplier": ["suplier"]
        },
        "invoice_columns": {
            "shipquantity": ["ShipQuantity"],
            "upc": ["Upc"],
            "price": ["NetEach2"],
            "packsize": ["PackSize"],
            "brand": ["Brand"],
            "description": ["Description"]
        }
    },
    "invoicefinder_yonergeler.txt": (
        "Invoice Finder Programı Yönergeleri:\n\n"
        "1. Ekranınızda gözükmekte olan ilk boşluğa orada da belirtildiği üzere uygulamanın bulmuş olduğu invoice dosyalarının ve en son uygulamanın oluşturacağı excel dosyasının kaydedileceği dosya yolunu gerek elinizle yazarak gerek Browse butonunu kullanarak uygulamaya belirtiniz.\n\n"
        "2. İkinci boşluğa ise bilgisayarınızda bulunan bütün invoice pdf dosyalarını içeren klasörün yolunu 1. yönergede belirtildiği şekilde giriniz.\n\n"
        "3. Üçüncü boşluğa ise içeriğinde bütün Upc değerleri ve o değerlere karşılık gelen invoice numaralarını içeren ALL INVOICES excelini önceki maddelerde belirtildiği şekilde giriniz.\n\n"
        "4. Dördüncü boşluğa ise uygulamanın hangi tarihten önceki invoiceleri tarayacağını giriniz.\n\n"
        "5. İlk 3 Dosya yolunu \"Kaydet\" butonu arayıcılığıyla daha sonraki işlemlerinizde de kullanmak amacıyla kaydedebilirsiniz.\n\n"
        "6. Bütün bu dosya yolu girme yerlerinin altında bir adet sürükle ve bırak yöntemi ile dosya algılayan alan göreceksiniz. O alana Amazonun sitesinden kopyalayarak aldığınız verileri bir excele metin olarak yapıştırıp oluşturduğunuz excel dosyasını belirtilen alana fare imlecinizle tutup bırakınız.\n\n"
        "7. İşlemi başlatmak için \"Başlat\" butonunuza basmanız yeterlidir.\n\n"
        "-------------SÜTUN İSİMLERİ---------------\n\n"
        "ALL INVOICES EXCEL DOSYASI İÇİN:\n\n"
        "ship quantity = ShipQuantity\n"
        "item number = ShipItem\n"
        "UPC = Upc\n"
        "Invoice Number = InvoiceNumber\n"
        "Date = Date"
    )
}


def ensure_default_settings():
    for filename, content in DEFAULT_SETTINGS.items():
        path = os.path.join(SETTINGS_DIR, filename)
        if not os.path.exists(path):
            if filename.endswith(".json"):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=4, ensure_ascii=False)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
    os.makedirs(os.path.join(SETTINGS_DIR, "Template"), exist_ok=True)


def read_settings_file(filename: str):
    filename = os.path.basename(filename)
    path = os.path.join(SETTINGS_DIR, filename)
    if not os.path.exists(path):
        return {} if filename.endswith(".json") else ""
    with open(path, "r", encoding="utf-8") as f:
        # JSON ise doğrudan dict dön, metinse raw text dön
        return json.load(f) if filename.endswith(".json") else f.read()


def write_settings_file(filename: str, content):
    filename = os.path.basename(filename)
    path = os.path.join(SETTINGS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        if filename.endswith(".json"):
            # Frontend'den string geldiyse json formatına geri çevirip diske yaz
            data = json.loads(content) if isinstance(content, str) else content
            json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            f.write(content)


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


KEYRING_SERVICE = "OperationsToolkit-2DWorkflow"


def get_saved_credentials():
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


class Api:
    def __init__(self):
        self._window = None
        self._cancel_event = Event()
        self._job_lock = Lock() # Concurrency Override Hatasını Engeller

    def set_window(self, window):
        self._window = window

    def cancel_job(self):
        self._cancel_event.set()
        self._emit("job-log", {"message": "İşlem kullanıcı tarafından iptal ediliyor...", "color": "red"})
        return True

    def _reset_cancel_flag(self):
        self._cancel_event.clear()

    def pick_files(self, file_types=None, multiple=True):
        types = tuple(file_types) if file_types else ()
        result = self._window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=multiple, file_types=types)
        return list(result) if result else []

    def pick_folder(self):
        result = self._window.create_file_dialog(dialog_type=webview.FileDialog.FOLDER)
        return result[0] if result else ""

    def open_folder(self, path):
        if not path or not os.path.exists(path):
            return
        if sys.platform == "win32":
            os.startfile(path)
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

    def list_settings_files(self):
        files = []
        if os.path.isdir(SETTINGS_DIR):
            for f in sorted(os.listdir(SETTINGS_DIR)):
                if f.endswith(".txt"):
                    files.append({"filename": f, "content": read_settings_file(f)})
        return files

    def reset_settings_to_default(self, filename):
        filename = os.path.basename(filename)
        if filename not in DEFAULT_SETTINGS:
            return False
        write_settings_file(filename, DEFAULT_SETTINGS[filename])
        return True

    def open_settings_folder(self):
        self.open_folder(SETTINGS_DIR)
        return True

    def _emit(self, channel, payload):
        if not self._window:
            return
        js = f"window.dispatchEvent(new CustomEvent('{channel}', {{detail: {json.dumps(payload)}}}))"
        try:
            self._window.evaluate_js(js)
        except Exception:
            pass

    def bind_dropzones(self):
        try:
            zones = self._window.dom.get_elements(".dropzone")
        except Exception:
            return
        for zone in zones:
            zone_id = zone.id
            zone.events.dragover += DOMEventHandler(lambda e: None, True, True)
            zone.events.drop += DOMEventHandler(lambda e, zid=zone_id: self._handle_drop(zid, e), True, True)

    def _handle_drop(self, zone_id, event):
        try:
            files = (event.get("dataTransfer") or {}).get("files", [])
            paths = [f.get("pywebviewFullPath") for f in files if f.get("pywebviewFullPath")]
            if paths:
                self._emit("files-dropped", {"zoneId": zone_id, "paths": paths})
        except Exception:
            pass

    # =======================================================================
    # FBA INVENTORY PRO API ENDPOINTS
    # =======================================================================
    
    def _get_inventory_db(self):
        # Veritabanını Settings klasöründe güvenli bir yere kaydet
        db_path = os.path.join(SETTINGS_BASE_DIR, "Settings", "fba_inventory.db")
        return DatabaseManager(db_path)

    def inv_import_master_excel(self, file_path):
        try:
            db = self._get_inventory_db()
            success, msg = db.import_babil_master_excel(file_path)
            return {"ok": success, "message": msg}
        except Exception as e:
            return {"ok": False, "message": f"Hata: {str(e)}"}

    def inv_import_picklist(self, file_paths):
        try:
            db = self._get_inventory_db()
            count, skipped = 0, []
            for f in file_paths:
                candidate_ids = ShipmentIDExtractor.extract_shipment_ids_from_file(f)
                if any(db.is_shipment_exists(c_id) for c_id in candidate_ids):
                    skipped.append(candidate_ids.pop() if candidate_ids else "Bilinmeyen")
                    continue
                header, items = PicklistParser.parse_picklist_file(f)
                if db.is_shipment_exists(header.shipment_id):
                    skipped.append(header.shipment_id)
                    continue
                db.add_picklist_shipment(header, items)
                count += 1
                
            msg = f"{count} dosya aktarıldı. "
            if skipped:
                msg += f"Atlanan (Mevcut) ID'ler: {', '.join(skipped)}"
            return {"ok": True, "message": msg}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    def inv_import_stock(self, file_path):
        try:
            db = self._get_inventory_db()
            if file_path.endswith('.csv'):
                try: df = pd.read_csv(file_path, encoding='utf-8')
                except: df = pd.read_csv(file_path, encoding='latin1')
            else:
                df = pd.read_excel(file_path)

            sku_col = 'Merchant SKU' if 'Merchant SKU' in df.columns else ('SKU' if 'SKU' in df.columns else df.columns[0])
            sum_cols = ['Available', 'FC transfer', 'FC Processing', 'Unfulfillable', 'Shipped', 'Receiving']
            has_formula = all(c in df.columns for c in sum_cols)
            
            stock_dict = {}
            for _, r in df.iterrows():
                s = str(r[sku_col]).strip()
                if not s or s.lower() == 'nan': continue
                if has_formula:
                    q = sum(int(pd.to_numeric(r[c], errors='coerce')) if pd.notnull(pd.to_numeric(r[c], errors='coerce')) else 0 for c in sum_cols)
                else:
                    qty_col = 'Total Units' if 'Total Units' in df.columns else ('QTY' if 'QTY' in df.columns else df.columns[1])
                    val = pd.to_numeric(r[qty_col], errors='coerce')
                    q = int(val) if pd.notnull(val) else 0
                stock_dict[s] = q

            db.update_amazon_stock(stock_dict)
            return {"ok": True, "message": f"Stok güncellendi ({len(stock_dict)} SKU)."}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    def inv_detect_missing_ids(self, file_path):
        try:
            extracted = ShipmentIDExtractor.extract_shipment_ids_from_file(file_path)
            if not extracted: return {"ok": False, "message": "FBA Shipment ID tespit edilemedi."}
            db = self._get_inventory_db()
            registered = db.get_all_registered_shipment_ids()
            missing = sorted(list(extracted - registered))
            return {"ok": True, "extracted": len(extracted), "missing": missing}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    def inv_detect_missing_ids_from_text(self, extracted_ids_list):
        """Accepts a list of FBA IDs (already extracted client-side) and checks which are missing from the DB."""
        try:
            extracted = set(i.upper().strip() for i in extracted_ids_list if i)
            if not extracted:
                return {"ok": False, "message": "Geçerli FBA Shipment ID bulunamadı."}
            db = self._get_inventory_db()
            registered = db.get_all_registered_shipment_ids()
            missing = sorted(list(extracted - registered))
            return {"ok": True, "extracted": len(extracted), "missing": missing}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    def inv_get_all_data(self):
        try:
            db = self._get_inventory_db()
            sirali, analiz = FIFOEngine.calculate_fifo(db.get_all_shipments_sorted_by_date(), db.get_amazon_stock_map())
            
            safe_sirali = []
            for item in sirali:
                # Eğer item bir dataclass ise dict'e çevir, değilse kopyala
                d_item = dataclasses.asdict(item) if dataclasses.is_dataclass(item) else dict(item)
                # JSON hatasını önlemek için datetime objesini string'e çevir veya sil
                if 'created_dt' in d_item:
                    d_item['created_dt'] = d_item['created_dt'].isoformat() if d_item['created_dt'] else None
                safe_sirali.append(d_item)
                
            safe_analiz = []
            for item in analiz:
                d_item = dataclasses.asdict(item) if dataclasses.is_dataclass(item) else dict(item)
                if 'created_dt' in d_item:
                    d_item['created_dt'] = d_item['created_dt'].isoformat() if d_item['created_dt'] else None
                safe_analiz.append(d_item)

            return {"ok": True, "sirali": safe_sirali, "analiz": safe_analiz, "stock": db.get_amazon_stock_map()}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    def inv_update_note(self, shipment_id, sku, exp_date_usa, note):
        try:
            self._get_inventory_db().update_item_note(shipment_id, sku, exp_date_usa, note)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    def inv_reset_data(self):
        try:
            self._get_inventory_db().reset_all_data()
            return {"ok": True, "message": "Veritabanı sıfırlandı."}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    def inv_export_excel(self, output_folder):
        try:
            today_str = datetime.now().strftime("%Y.%m.%d")
            file_path = os.path.join(output_folder, f"Expration Date Analizi_{today_str}.xlsx")
            ExcelReportExporter.export_master_excel(file_path, self._get_inventory_db())
            return {"ok": True, "path": file_path}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    # -- İşlem Yürütme Modülleri (Thread-Safe ve İptal Destekli) --

    def run_converter(self, files, output_folder, input_type, output_type):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var. Lütfen bitmesini bekleyin.", "color": "red"})
            return False
        
        self._reset_cancel_flag()
        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_conversion(files, output_folder, input_type, output_type, progress_callback=progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_costupdater(self, input_file, output_folder, settings_content, version):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg, color="white"):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg, "color": color})
        
        if isinstance(settings_content, str):
            try:
                settings_content = json.loads(settings_content)
            except json.JSONDecodeError:
                self._job_lock.release()
                self._emit("job-done", {"ok": False, "message": "Geçersiz JSON formatı. Ayar dosyası bozuk."})
                return False

        def worker():
            try:
                result = process_costupdater(input_file, output_folder, settings_content, version=version, progress_callback=progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result.get("output_path", output_folder)})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_restock(self, row_files, export_files, restock_files, do_export, do_restock, save_name, output_folder, settings_dict):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg, percent=None):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg, "percent": percent})

        islem = {"export": 1 if do_export else 0, "restock": 1 if do_restock else 0}

        def worker():
            try:
                # settings_path yerine settings_dict gönderiliyor
                result = process_restock_logic(output_folder, row_files, export_files, restock_files, islem, save_name, settings_dict, progress)
                self._emit("job-done", {"ok": True, "message": result.get("message", "Tamamlandı!"), "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_tsv(self, files, output_folder, save_name):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def emit_with_cancel(channel, payload):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit(channel, payload)

        def worker():
            try:
                total = len(files)
                tsv_settings = os.path.join(SETTINGS_DIR, "tsv_settings.txt")
                son_path = process_tsvs_and_aggregate(files=files, target_path=output_folder, settings_path=tsv_settings, emit_callback=emit_with_cancel)
                self._emit("job-done", {"ok": True, "message": f"{total} file(s) processed and aggregated directly to son.xlsx.", "output_path": output_folder})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_invoice(self, files, output_folder, settings_dict, delete_zeros):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_invoice(files, output_folder, settings_dict, delzero=1 if delete_zeros else 0, progress_callback=progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def open_template_folder(self):
        folder = os.path.join(SETTINGS_DIR, "Template")
        os.makedirs(folder, exist_ok=True)
        self.open_folder(folder)

    def run_order_create(self, restock_files, orderform_files, output_folder, settings_dict):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        template_path = os.path.join(SETTINGS_DIR, "Template", "Template.xlsx")

        def worker():
            try:
                result = process_order_create(restock_files, orderform_files, template_path, output_folder, settings_dict, progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_shipment_creator(self, invoice_files, orderform_files, restock_files, dc_code, save_name, output_folder, settings_dict):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_shipment_creation(invoice_files, orderform_files, restock_files, output_folder, save_name, dc_code, settings_dict, progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_future_price(self, restock_file, future_file, save_name, output_folder):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_future_price(output_folder, save_name, restock_file, future_file, progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_pk_extractor(self, file_path):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()

        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                progress("İşlem başlatılıyor...")
                total, modified, out_path = PKExtractorEngine.process_file(file_path, progress_callback=progress)
                
                success_msg = f"İşlem başarıyla tamamlandı! Toplam Satır: {total} | Değişen PK: {modified}"
                self._emit("job-done", {"ok": True, "message": success_msg, "output_path": out_path})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def get_invoice_finder_instructions(self):
        return read_settings_file("invoicefinder_yonergeler.txt")

    def run_invoice_finder_date_mode(self, source_excel, all_invoices_excel, invoice_pdf_folder, output_folder, user_input_date):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_invoice_finder(source_excel, all_invoices_excel, invoice_pdf_folder, output_folder, user_input_date, progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def run_invoice_finder_upc_mode(self, all_invoices_excel, invoice_pdf_folder, output_folder, upcs_str, months_str):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg})

        def worker():
            try:
                result = process_invoice_finder_upc(all_invoices_excel, invoice_pdf_folder, output_folder, upcs_str, months_str, progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True

    def get_expiration_credentials(self):
        username, password = get_saved_credentials()
        return {"username": username, "password": password}

    def save_expiration_credentials(self, username, password):
        save_credentials(username, password)
        return True

    def run_expiration(self, username, password, item_ids_str, output_folder, remember):
        if not self._job_lock.acquire(blocking=False):
            self._emit("job-log", {"message": "Sistemde zaten çalışan bir işlem var.", "color": "red"})
            return False

        self._reset_cancel_flag()
        def progress(msg, color="white"):
            if self._cancel_event.is_set():
                raise InterruptedError("İşlem iptal edildi.")
            self._emit("job-log", {"message": msg, "color": color})

        if remember:
            save_credentials(username, password)
        settings_path = os.path.join(SETTINGS_DIR, "expration_settings.txt")
        
        def worker():
            try:
                result = process_expiration(username, password, item_ids_str, output_folder, settings_path, progress)
                self._emit("job-done", {"ok": True, "message": result["message"], "output_path": result["output_path"]})
            except InterruptedError:
                self._emit("job-done", {"ok": False, "message": "İşlem kullanıcı tarafından durduruldu."})
            except Exception as e:
                self._emit("job-done", {"ok": False, "message": str(e)})
            finally:
                self._job_lock.release()

        Thread(target=worker, daemon=True).start()
        return True
    def get_current_version(self):
        return CURRENT_VERSION
    
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
        subprocess.Popen([batch_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def run_check_for_updates(self):
        def worker():
            if not self.check_internet():
                self._emit("update-status", {"state": "no-internet"})
                return
            data = self.get_latest_release()
            if not data:
                self._emit("update-status", {"state": "check-failed"})
                return
            latest = data.get("tag_name", "")
            if version.parse(latest) > version.parse(CURRENT_VERSION):
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
        def worker():
            time.sleep(1)
            if not self.check_internet():
                return
            data = self.get_latest_release()
            if not data:
                return
            latest = data.get("tag_name", "")
            if version.parse(latest) > version.parse(CURRENT_VERSION):
                self._emit("update-badge", {
                    "version": latest,
                    "notes": data.get("body", ""),
                    "assets": [{"name": a["name"], "browser_download_url": a["browser_download_url"]} for a in data.get("assets", [])],
                })
        Thread(target=worker, daemon=True).start()

    def run_download_update(self, url):
        def worker():
            current_os = platform.system()
            
            # WINDOWS MANTIĞI: Sessiz indirme ve BAT ile kurulum
            if current_os == "Windows":
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
                Thread(target=self._delayed_exit, daemon=True).start()

            # MACOS VE LINUX MANTIĞI: Güvenli Tarayıcı Yönlendirmesi
            else:
                self._emit("update-download-progress", {"percent": 100, "message": "Opening download page in your browser..."})
                import webbrowser
                # Doğrudan releases sayfasına yönlendir, kullanıcı Mac/Linux dosyasını kendi indirsin
                webbrowser.open("https://github.com/hasanaliduruk/KWIEKLLCREFACTOR/releases")
                
                # Kullanıcının işlemi manuel yapması için 3 saniye sonra UI'ı normale döndür
                time.sleep(3)
                self._emit("update-download-progress", {"percent": 100, "message": "Please install the downloaded file manually."})
                
        Thread(target=worker, daemon=True).start()

    def _delayed_exit(self):
        time.sleep(3)
        os._exit(0)


def _inject_icon_data_uri(window, icon_path):
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
    if platform.system() == "Windows":
        try:
            # Windows 10/11 Per-Monitor DPI Awareness tetikleyicisi
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # Eski Windows versiyonları için Fallback
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
        os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = "--force-device-scale-factor=1"
    ensure_default_settings()

    api = Api()
    index_path = os.path.join(APP_DIR, "gui_web", "index.html")
    icon_path = get_asset_path("icon.ico")

    state = load_window_state()

    window = webview.create_window(
        "Operations Toolkit",
        index_path,
        js_api=api,
        width=state.get("width", 1280),
        height=state.get("height", 860),
        x=state.get("x"),
        y=state.get("y"),
        min_size=(960, 640),
        background_color="#15171c"
    )
    api.set_window(window)

    window_status = {"is_maximized": state.get("maximized", False)}

    def on_maximized():
        window_status["is_maximized"] = True

    def on_restored():
        window_status["is_maximized"] = False

    # Pencere kapanırken son durumu (koordinatları ve boyutu) diske yaz
    def on_closing():
        save_window_state(window, window_status["is_maximized"])

    def on_loaded():
        api.bind_dropzones()
        _inject_icon_data_uri(window, icon_path)
        api.run_silent_update_check()
        
        # Eğer uygulama en son tam ekran (maximize) olarak kapatıldıysa, tekrar o şekilde başlat
        if window_status["is_maximized"]:
            window.maximize()

    window.events.maximized += on_maximized
    window.events.restored += on_restored
    window.events.closing += on_closing
    window.events.loaded += on_loaded

    webview.start(debug=False, icon=icon_path)

if __name__ == "__main__":
    main()