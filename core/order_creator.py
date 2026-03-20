import os
import pandas as pd
import openpyxl


def parse_order_settings(settings_content: str):
    sutunlar_dict = {
        "restock_upc": [],
        "restock_pcs": [],
        "restock_suplier": [],
        "restock_notes": [],
        "orderform_upc": [],
        "orderform_pcs": [],
        "orderform_suplier": [],
    }
    lines = [line.strip() for line in settings_content.split("\n") if line.strip()]
    a = 0
    for line in lines:
        if "=====" in line:
            a += 1
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip().lower()
            vals = [v.strip() for v in val.split(",")]

            if a == 0:  # RESTOCK
                if key == "upc":
                    sutunlar_dict["restock_upc"] = vals
                elif key == "pcs":
                    sutunlar_dict["restock_pcs"] = vals
                elif key == "suplier":
                    sutunlar_dict["restock_suplier"] = vals
                elif key == "notes":
                    sutunlar_dict["restock_notes"] = vals
            elif a == 1:  # ORDER FORM
                if key == "upc":
                    sutunlar_dict["orderform_upc"] = vals
                elif key == "pcs":
                    sutunlar_dict["orderform_pcs"] = vals
                elif key == "suplier":
                    sutunlar_dict["orderform_suplier"] = vals
    return sutunlar_dict


def check_column(df, possible_cols, file_name, col_type):
    for col in possible_cols:
        if col in df.columns:
            return col
    raise ValueError(
        f"Eksik Sütun Hatası: '{file_name}' dosyasında '{col_type}' sütunu bulunamadı. Beklenenler: {possible_cols}"
    )


def process_order_create(
    restock_files: list,
    orderform_files: list,
    template_path: str,
    output_folder: str,
    settings_content: str,
    progress_callback=None,
) -> dict:
    if not restock_files:
        raise FileNotFoundError("Hata: Restock excel dosyası sağlanmadı.")
    if not orderform_files:
        raise FileNotFoundError("Hata: Order Form excel dosyası sağlanmadı.")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Hata: Template dosyası bulunamadı -> {template_path}")

    sutunlar_dict = parse_order_settings(settings_content)
    output_dictionary = {}

    # 1. RESTOCK İŞLEMLERİ
    if progress_callback:
        progress_callback("Restock excel dosyası okunuyor...")
    df_restock = pd.read_excel(restock_files[0]).fillna(0)

    upc_col = check_column(df_restock, sutunlar_dict["restock_upc"], "Restock", "UPC")
    pcs_col = check_column(df_restock, sutunlar_dict["restock_pcs"], "Restock", "PCS")
    suplier_col = check_column(
        df_restock, sutunlar_dict["restock_suplier"], "Restock", "SUPLIER"
    )
    notes_col = check_column(
        df_restock, sutunlar_dict["restock_notes"], "Restock", "NOTES"
    )

    upc_values = df_restock[upc_col].tolist()
    pcs_values = df_restock[pcs_col].tolist()
    suplier_values = df_restock[suplier_col].tolist()
    notes_values = df_restock[notes_col].tolist()

    for i, a in enumerate(upc_values):
        if pcs_values[i] != 0:
            sup = suplier_values[i]
            if sup not in output_dictionary:
                output_dictionary[sup] = {}
            if a not in output_dictionary[sup]:
                output_dictionary[sup][a] = 0
            output_dictionary[sup][a] += pcs_values[i]

            note = notes_values[i]
            if note != 0:
                if note not in output_dictionary:
                    output_dictionary[note] = {}
                if a not in output_dictionary[note]:
                    output_dictionary[note][a] = 0
                output_dictionary[note][a] += pcs_values[i]

    # 2. ORDER FORM İŞLEMLERİ
    if progress_callback:
        progress_callback("Order Form excel dosyası okunuyor...")
    df_order = pd.read_excel(orderform_files[0]).fillna(0)

    o_upc_col = check_column(
        df_order, sutunlar_dict["orderform_upc"], "Order Form", "UPC"
    )
    o_pcs_col = check_column(
        df_order, sutunlar_dict["orderform_pcs"], "Order Form", "PCS"
    )
    o_sup_col = check_column(
        df_order, sutunlar_dict["orderform_suplier"], "Order Form", "SUPLIER"
    )

    o_upc_values = df_order[o_upc_col].tolist()
    o_pcs_values = df_order[o_pcs_col].tolist()
    o_sup_values = df_order[o_sup_col].tolist()

    for i, a in enumerate(o_upc_values):
        if o_pcs_values[i] != 0:
            sup = o_sup_values[i]
            if sup not in output_dictionary:
                output_dictionary[sup] = {}
            if a not in output_dictionary[sup]:
                output_dictionary[sup][a] = 0
            output_dictionary[sup][a] += o_pcs_values[i]

    # 3. ŞABLONA YAZDIRMA
    target_dir = os.path.join(output_folder, "ORDERS")
    os.makedirs(target_dir, exist_ok=True)

    if progress_callback:
        progress_callback("Bulunan değerler template dosyalarına yazdırılıyor...")

    for suplier in output_dictionary.keys():
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active
        start_row = 2
        for i, upc in enumerate(output_dictionary[suplier].keys()):
            ws.cell(row=start_row + i, column=1, value=upc)
            ws.cell(row=start_row + i, column=3, value=output_dictionary[suplier][upc])
            ws[f"A{start_row+i}"].number_format = "000000000000"

        # Dosya ismini temizle (Geçersiz karakterleri önlemek için)
        safe_suplier = str(suplier).replace("/", "-").replace("\\", "-").upper()
        output_path = os.path.join(target_dir, f"{safe_suplier}.xlsx")
        wb.save(output_path)

    return {
        "status": "success",
        "message": "Order Create işlemi başarıyla tamamlandı!",
        "output_path": target_dir,
    }
