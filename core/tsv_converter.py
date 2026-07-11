import csv
import os
import glob
import pandas as pd
import openpyxl
from xlsxwriter import Workbook


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


def convert_tsv_to_excel(
    file_path: str,
    target_path: str,
    target_name: str,
    settings_path: str = None,
) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Hata: Belirtilen dosya bulunamadı -> {file_path}")

    if target_name == "" or target_name == " " or target_name is None:
        target_name = "Converted_File"

    if not target_name.endswith(".xlsx"):
        target_name += ".xlsx"

    os.makedirs(target_path, exist_ok=True)
    full_target_path = os.path.join(target_path, target_name)

    # Header detection: skip rows until a header row containing one of the
    # configured columns is found, then write every following row. This
    # restores the behaviour of the original tsv_script() (xlsx_converter).
    columns = _read_tsv_settings(settings_path)

    try:
        workbook = Workbook(full_target_path)
        worksheet = workbook.add_worksheet()

        with open(file_path, "rt", encoding="utf8") as f:
            reader = csv.reader(f, delimiter="\t")
            header_found = False
            row1 = 0
            for row in reader:
                if not header_found:
                    for col in columns:
                        if col in row:
                            header_found = True
                            break
                if header_found:
                    worksheet.write_row(row1, 0, row)
                    row1 += 1
        workbook.close()

        wb = openpyxl.load_workbook(full_target_path)
        sheet = wb.active
        for column_cells in sheet.columns:
            length = max(len(str(cell.value) or "") for cell in column_cells)
            sheet.column_dimensions[
                openpyxl.utils.get_column_letter(column_cells[0].column)
            ].width = (length + 3)
        wb.save(full_target_path)

        return {
            "status": "success",
            "message": "Conversion Completed Successfully.",
            "output_path": full_target_path,
        }

    except Exception as e:
        raise RuntimeError(f"Dönüştürme sırasında mantıksal bir hata oluştu: {str(e)}")


def compare_and_write(target_path: str) -> str:
    """Aggregate every produced xlsx in `target_path`: sum `Shipped` per
    `Merchant SKU` and write the combined result to `son.xlsx`.

    Restores the original tsv_script() compare_and_write() step.
    """
    files = [
        f for f in glob.glob(os.path.join(target_path, "*.xlsx"))
        if os.path.basename(f).lower() != "son.xlsx"
    ]
    if not files:
        raise RuntimeError("Hata: Birleştirilecek dönüştürülmüş dosya bulunamadı.")

    aggregated = {}
    for f in files:
        df = pd.read_excel(f)
        if "Merchant SKU" not in df.columns or "Shipped" not in df.columns:
            continue
        skus = df["Merchant SKU"].tolist()
        shipped = df["Shipped"].tolist()
        for i, sku in enumerate(skus):
            try:
                aggregated[sku] = aggregated.get(sku, 0) + float(shipped[i])
            except (ValueError, TypeError):
                pass

    result = pd.DataFrame({
        "Merchant SKU": list(aggregated.keys()),
        "Shipped": list(aggregated.values()),
    })
    out_path = os.path.join(target_path, "son.xlsx")
    result.to_excel(out_path, index=False)
    return out_path
