import os
import math
import pandas as pd
import numpy as np

def get_col(df, possible_cols, context):
    for col in possible_cols:
        if col in df.columns:
            return col
    raise ValueError(f"Eksik Sütun: {context} için beklenen sütunlardan hiçbiri bulunamadı. Beklenenler: {possible_cols}")


def clean_upc(series):
    return series.astype(str).str.split('.').str[0].str.strip().str.zfill(12)


def process_shipment_creation(
    invoice_files: list, order_form_files: list, restock_files: list,
    output_folder: str, save_name: str, dc_code: str,
    settings_dict: dict, progress_callback=None,
) -> dict:
    if not invoice_files or not order_form_files or not restock_files:
        raise ValueError("Hata: Gerekli kaynak dosyalardan biri eksik.")

    sutunlar_dict = {
        "restock_upc": settings_dict.get("restock_columns", {}).get("upc", []),
        "restock_pcs": settings_dict.get("restock_columns", {}).get("pcs", []),
        "restock_asin": settings_dict.get("restock_columns", {}).get("asin", []),
        "restock_pk": settings_dict.get("restock_columns", {}).get("pk", []),
        "restock_price": settings_dict.get("restock_columns", {}).get("price", []),
        "restock_suplier": settings_dict.get("restock_columns", {}).get("suplier", []),
        "orderform_upc": settings_dict.get("orderform_columns", {}).get("upc", []),
        "orderform_pcs": settings_dict.get("orderform_columns", {}).get("pcs", []),
        "orderform_asin": settings_dict.get("orderform_columns", {}).get("asin", []),
        "orderform_sku": settings_dict.get("orderform_columns", {}).get("sku", []),
        "orderform_pk": settings_dict.get("orderform_columns", {}).get("pk", []),
        "orderform_price": settings_dict.get("orderform_columns", {}).get("price", []),
        "orderform_suplier": settings_dict.get("orderform_columns", {}).get("suplier", []),
        "invoice_shipquantity": settings_dict.get("invoice_columns", {}).get("shipquantity", []),
        "invoice_upc": settings_dict.get("invoice_columns", {}).get("upc", []),
        "invoice_price": settings_dict.get("invoice_columns", {}).get("price", []),
        "invoice_packsize": settings_dict.get("invoice_columns", {}).get("packsize", []),
        "invoice_brand": settings_dict.get("invoice_columns", {}).get("brand", []),
        "invoice_description": settings_dict.get("invoice_columns", {}).get("description", []),
    }

    # 1. INVOICE VERİSİ (Vektörel Format)
    if progress_callback: progress_callback("Invoice dosyası işleniyor...")
    df_inv_raw = pd.read_excel(invoice_files[0])
    df_inv = pd.DataFrame()
    
    # GİZLİ İNDEKS: Orijinal Invoice satır sırasını takip etmek için
    df_inv["_orig_idx"] = np.arange(len(df_inv_raw))
    
    df_inv["UPC"] = clean_upc(df_inv_raw[get_col(df_inv_raw, sutunlar_dict["invoice_upc"], "Invoice UPC")])
    df_inv["ShipQuantity"] = df_inv_raw[get_col(df_inv_raw, sutunlar_dict["invoice_shipquantity"], "Invoice ShipQuantity")]
    df_inv["Price"] = df_inv_raw[get_col(df_inv_raw, sutunlar_dict["invoice_price"], "Invoice Price")]
    df_inv["PackSize"] = df_inv_raw[get_col(df_inv_raw, sutunlar_dict["invoice_packsize"], "Invoice PackSize")]
    df_inv["Brand"] = df_inv_raw[get_col(df_inv_raw, sutunlar_dict["invoice_brand"], "Invoice Brand")]
    df_inv["Description"] = df_inv_raw[get_col(df_inv_raw, sutunlar_dict["invoice_description"], "Invoice Description")]

    # 2. RESTOCK VERİSİ (Vektörel Format)
    if progress_callback: progress_callback("Restock dosyası işleniyor...")
    df_res_raw = pd.read_excel(restock_files[0])
    df_res = pd.DataFrame()
    df_res["UPC"] = clean_upc(df_res_raw[get_col(df_res_raw, sutunlar_dict["restock_upc"], "Restock UPC")])
    df_res["Price Check"] = df_res_raw[get_col(df_res_raw, sutunlar_dict["restock_price"], "Restock Price")]
    df_res["Suplier"] = df_res_raw[get_col(df_res_raw, sutunlar_dict["restock_suplier"], "Restock Suplier")]
    df_res["Asin"] = df_res_raw[get_col(df_res_raw, sutunlar_dict["restock_asin"], "Restock ASIN")]
    df_res["Pcs"] = df_res_raw[get_col(df_res_raw, sutunlar_dict["restock_pcs"], "Restock PCS")]
    df_res["PK"] = df_res_raw[get_col(df_res_raw, sutunlar_dict["restock_pk"], "Restock PK")]
    df_res["SKU"] = "#YOK"
    df_res["DOSYA"] = "Restock"
    df_res = df_res[df_res["Pcs"].notna()].copy()
    raw_res_upcs = set(df_res["UPC"])

    # 3. ORDER FORM VERİSİ (Vektörel - Uzun Formata Çevirme (Melt) İşlemi)
    if progress_callback: progress_callback("Order Form dosyası işleniyor...")
    df_ord_raw = pd.read_excel(order_form_files[0])
    ord_frames = []
    raw_ord_upcs = set(clean_upc(df_ord_raw[get_col(df_ord_raw, sutunlar_dict["orderform_upc"], "OrderForm UPC")]))
    
    for i in range(len(sutunlar_dict["orderform_asin"])):
        try:
            asin_name = sutunlar_dict["orderform_asin"][i]
            sku_name = sutunlar_dict["orderform_sku"][i]
            pcs_name = sutunlar_dict["orderform_pcs"][0] if i == 0 else f"{sutunlar_dict['orderform_pcs'][0]}.{i}"
            
            temp = pd.DataFrame()
            temp["UPC"] = clean_upc(df_ord_raw[get_col(df_ord_raw, sutunlar_dict["orderform_upc"], "OrderForm UPC")])
            temp["Price Check"] = df_ord_raw[get_col(df_ord_raw, sutunlar_dict["orderform_price"], "OrderForm Price")]
            temp["Suplier"] = df_ord_raw[get_col(df_ord_raw, sutunlar_dict["orderform_suplier"], "OrderForm Suplier")]
            temp["Asin"] = df_ord_raw[get_col(df_ord_raw, [asin_name], f"ASIN {i+1}")]
            temp["Pcs"] = df_ord_raw[get_col(df_ord_raw, [pcs_name], f"PCS {i+1}")]
            temp["SKU"] = df_ord_raw[get_col(df_ord_raw, sutunlar_dict["orderform_sku"], f"SKU {i+1}")]
            sku_series = temp["SKU"].fillna("").astype(str)
            
            temp["PK"] = sku_series.apply(
                lambda x: x.split('_')[2] if "_" in x and x.count('_') >= 3 else "#YOK"
            )
            temp["DOSYA"] = "Order Form"
            temp = temp[temp["Asin"].notna()].copy()
            ord_frames.append(temp)
        except ValueError:
            break
            
    df_ord = pd.concat(ord_frames, ignore_index=True) if ord_frames else pd.DataFrame(columns=df_res.columns)

    # 4. EŞLEŞTİRME (Vektörel LEFT/INNER JOIN Algoritması)
    if progress_callback: progress_callback("O(1) Hızında İlişkisel Eşleşme (Join) yapılıyor...")
    
    matched_res = df_inv.merge(df_res, on="UPC", how="inner")
    matched_ord = df_inv.merge(df_ord, on="UPC", how="inner")
    
    df_empty_res = df_inv[df_inv["UPC"].isin(raw_res_upcs) & ~df_inv["UPC"].isin(matched_res["UPC"])].copy()
    df_empty_res["DOSYA"] = "Restock"
    
    df_empty_ord = df_inv[df_inv["UPC"].isin(raw_ord_upcs) & ~df_inv["UPC"].isin(matched_ord["UPC"])].copy()
    df_empty_ord["DOSYA"] = "Order Form"
    
    df_unmatched = df_inv[~df_inv["UPC"].isin(raw_res_upcs) & ~df_inv["UPC"].isin(raw_ord_upcs)].copy()
    df_unmatched["DOSYA"] = "#YOK"
    
    # HİYERARŞİK SIRALAMA ÖNCELİKLERİ
    matched_res["_sort_prio"] = 1
    matched_ord["_sort_prio"] = 2
    df_empty_res["_sort_prio"] = 3
    df_empty_ord["_sort_prio"] = 4
    df_unmatched["_sort_prio"] = 5
    
    final_df = pd.concat([matched_res, matched_ord, df_empty_res, df_empty_ord, df_unmatched], ignore_index=True)
    
    for c in ["Price Check", "Suplier", "Asin", "Pcs", "PK", "SKU"]:
        if c not in final_df.columns: 
            final_df[c] = "#YOK"

    # ORİJİNAL İNVOİCE SIRALAMASINI GERİ YÜKLE
    # Aynı satırdan çoğalanları (birden fazla Asin eşleşmesi vs.) aralarında _sort_prio'ya göre diz
    final_df.sort_values(by=["_orig_idx", "_sort_prio"], inplace=True)
    final_df.reset_index(drop=True, inplace=True)

    # SKU2 HESAPLAMASI (Vektörel)
    valid_mask = (final_df["PK"] != "#YOK") & (final_df["Price"] != "#YOK")
    pk_ints = final_df.loc[valid_mask, "PK"].astype(str).str.replace("PK", "").astype(float).fillna(0).astype(int)
    prices = pd.to_numeric(final_df.loc[valid_mask, "Price"], errors='coerce')
    upc_strs = final_df.loc[valid_mask, "UPC"].astype(str)
    
    calc_vals = pk_ints * prices
    final_df["SKU2"] = "#YOK"
    final_df.loc[valid_mask, "SKU2"] = dc_code + "_" + upc_strs + "_" + final_df.loc[valid_mask, "PK"].astype(str) + "_" + calc_vals.map(lambda x: format(x, '.2f'))

    # SKU2 Çoğullama Harfleri (A, B, C)
    is_valid_sku2 = final_df["SKU2"] != "#YOK"
    cum_counts = final_df[is_valid_sku2].groupby("SKU2").cumcount()
    letters = {0: "", 1: "_A", 2: "_B", 3: "_C", 4: "_D", 5: "_E"}
    final_df.loc[is_valid_sku2, "SKU2"] = final_df.loc[is_valid_sku2, "SKU2"] + cum_counts.map(lambda x: letters.get(x, f"_{x}"))

    # 5. STOCK ALLOCATER (Vektörel Window Functions)
    if progress_callback: progress_callback("Stoklar vektörel olarak dağıtılıyor...")
    
    final_df["Yeni Pcs"] = 0
    final_df["PK EACH"] = 0
    final_df["Kalan"] = 0
    
    final_df["Num_Pcs"] = pd.to_numeric(final_df["Pcs"], errors="coerce").fillna(0)
    final_df["Num_ShipQty"] = pd.to_numeric(final_df["ShipQuantity"], errors="coerce").fillna(0)
    final_df["Num_PK"] = final_df["PK"].astype(str).str.replace("PK", "").apply(pd.to_numeric, errors="coerce")
    final_df["Has_PK"] = final_df["Num_PK"].notna() & (final_df["PK"] != "#YOK")
    
    total_pcs = final_df.groupby("UPC")["Num_Pcs"].transform("sum")
    base_new_pcs = np.round((final_df["Num_Pcs"] / total_pcs.replace(0, np.nan)) * final_df["Num_ShipQty"]).fillna(0)
    
    kalan = base_new_pcs % final_df["Num_PK"]
    kalan = np.where(final_df["Has_PK"], kalan.fillna(0), 0)
    
    final_df["Yeni Pcs"] = np.where(final_df["Has_PK"], base_new_pcs - kalan, base_new_pcs)
    
    valid_pk_df = final_df[final_df["Has_PK"]].copy()
    valid_pk_df["RowIdx"] = valid_pk_df.index
    
    sorted_pk = valid_pk_df.sort_values(by=["UPC", "Num_PK", "RowIdx"], ascending=[True, True, False])
    smallest_pk_idx = sorted_pk.groupby("UPC").head(1).set_index("UPC")["RowIdx"]
    
    final_df["_temp_kalan"] = kalan
    total_kalan_per_upc = final_df.groupby("UPC")["_temp_kalan"].sum()
    
    for upc, idx in smallest_pk_idx.items():
        if upc in total_kalan_per_upc.index:
            final_df.at[idx, "Yeni Pcs"] += total_kalan_per_upc[upc]
            
    if "_temp_kalan" in final_df.columns:
        final_df.drop(columns=["_temp_kalan"], inplace=True)
            
    final_df["PK EACH"] = np.where(final_df["Has_PK"], final_df["Yeni Pcs"] // final_df["Num_PK"].replace(0, np.nan), 0)
    final_df["Kalan"] = np.where(final_df["Has_PK"], final_df["Yeni Pcs"] % final_df["Num_PK"].replace(0, np.nan), 0)
    
    # Sütun Sıralaması (Gizli indeksler `_orig_idx` ve `_sort_prio` Excel'e basılmaz, otomatik temizlenir)
    final_columns = [
        "UPC", "Price", "Price Check", "Suplier", "ShipQuantity", "Asin", "Pcs", 
        "Yeni Pcs", "PK", "SKU", "PackSize", "Brand", "Description", "DOSYA", 
        "SKU2", "PK EACH", "Kalan"
    ]
    final_df = final_df[final_columns].copy()

    final_df = final_df[final_columns].fillna("#YOK")

    # 6. EXCEL'E KAYIT
    if progress_callback: progress_callback("Sonuç Excel dosyasına kaydediliyor...")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{save_name}.xlsx")
    final_df.to_excel(output_path, index=False)

    return {
        "status": "success",
        "message": "Shipment Create işlemi vektörel hızda başarıyla tamamlandı!",
        "output_path": output_folder,
    }
    