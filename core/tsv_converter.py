import csv
import os
import glob
import pandas as pd
import openpyxl
from xlsxwriter import Workbook
from typing import List, Callable


def _read_tsv_settings(settings_path: str):
    """Read the `columns = ...` list from Settings/tsv_settings.txt.

    Falls back to the original default column list if the file is missing
    or has no `columns=` line (same behaviour as the old tkinter app).
    """
    default_columns = [
        "Merchant SKU", "Title", "ASIN", "FNSKU",
        "external-id", "Condition", "Shipped",
    ]
    if not settings_path or not os.path.exists(settings_path):
        return default_columns
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if line.lower().startswith("columns"):
                    _, val = line.split("=", 1)
                    cols = [c.strip() for c in val.split(",") if c.strip()]
                    return cols or default_columns
    except Exception:
        pass
    return default_columns


def process_tsvs_and_aggregate(files: List[str], target_path: str, settings_path: str = None, emit_callback: Callable = None) -> str:
    """
    Reads a provided list of TSV files directly into memory, aggregates 'Shipped' quantities,
    emits progress, and writes only the final son.xlsx file.
    """
    if not files:
        raise ValueError("Hata: İşlenecek dosya listesi boş.")

    columns_to_look_for = _read_tsv_settings(settings_path) # Assumes _read_tsv_settings is defined as before
    aggregated = {}
    total_files = len(files)

    for i, file_path in enumerate(files, start=1):
        if emit_callback:
            emit_callback("job-log", {"message": f"Processing in-memory ({i}/{total_files}): {os.path.basename(file_path)}"})
            
        with open(file_path, "rt", encoding="utf8") as f:
            reader = csv.reader(f, delimiter="\t")
            header = None
            sku_idx = -1
            shipped_idx = -1

            for row in reader:
                if header is None:
                    if any(col in row for col in columns_to_look_for):
                        header = row
                        try:
                            sku_idx = header.index("Merchant SKU")
                            shipped_idx = header.index("Shipped")
                        except ValueError:
                            break 
                else:
                    if len(row) > max(sku_idx, shipped_idx):
                        sku = row[sku_idx].strip()
                        try:
                            val = float(row[shipped_idx])
                            aggregated[sku] = aggregated.get(sku, 0.0) + val
                        except ValueError:
                            pass

    if not aggregated:
        raise RuntimeError("Hata: Hiçbir veriden geçerli 'Merchant SKU' ve 'Shipped' eşleşmesi çıkarılamadı.")

    if emit_callback:
        emit_callback("job-log", {"message": "Veriler bellekte birleştirildi. Disk'e yazılıyor (son.xlsx)..."})

    os.makedirs(target_path, exist_ok=True)
    out_path = os.path.join(target_path, "son.xlsx")
    
    df = pd.DataFrame({
        "Merchant SKU": list(aggregated.keys()),
        "Shipped": list(aggregated.values())
    })
    
    df.to_excel(out_path, index=False)
    return target_path
