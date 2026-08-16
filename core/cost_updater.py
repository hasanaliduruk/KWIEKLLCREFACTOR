import os
import pandas as pd
import numpy as np


def parse_settings(settings_content: str, version: int):
    columns_dictionary = {
        "cost": [], "additional cost": [], "bp strategy": [],
        "qd strategy": [], "business pricing": [], "sku": [],
    }
    if version == 2:
        columns_dictionary["pkg volume"] = []
        columns_dictionary["pkg weight"] = []

    maliyet_dictionary = {}
    lines_list = [line.strip() for line in settings_content.split("\n") if line.strip()]

    parsing_maliyet = False
    for line in lines_list:
        if "=====" in line:
            parsing_maliyet = True
            continue

        if not parsing_maliyet:
            if "=" in line:
                key, vals = line.split("=", 1)
                key = key.strip().lower()
                if key in columns_dictionary:
                    columns_dictionary[key] = [v.strip() for v in vals.split(",")]
        else:
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                if version == 1:
                    maliyet_dictionary[key] = val.replace(" ", "")
                else:
                    values = val.lstrip().split(" ")
                    if len(values) >= 3:
                        maliyet_dictionary[key] = {
                            "v2_additional_cost": float(values[0]),
                            "v2_equation": int(values[1]),
                            "v2_warehouse_fee": float(values[2]),
                        }

    return columns_dictionary, maliyet_dictionary


def check_columns(df, liste, isim):
    for col in liste:
        if col in df.columns:
            return col
    raise ValueError(
        f"Eksik Sütun Hatası: Yüklenen CSV dosyasında '{isim}' için beklenen sütunlardan hiçbiri bulunamadı. "
        f"Beklenen sütun adları: {liste}."
    )

def extract_price_vectorized(sku_series):
    def get_price(sku_str):
        parts = str(sku_str).split("_")[1:]
        price = np.nan
        for p in parts:
            p = p.replace(",", ".")
            try:
                price = float(p)
            except ValueError:
                pass
        return price
    return sku_series.apply(get_price)


def process_costupdater(
    input_file: str, output_folder: str, settings_content: str, version: int, progress_callback=None
) -> dict:
    if not input_file or not os.path.exists(input_file):
        raise FileNotFoundError("Hata: İşlenecek CSV dosyası bulunamadı.")

    columns_dictionary = settings_dict.get("columns", {})
    maliyet_dictionary = settings_dict.get("warehouses", {})

    if progress_callback:
        progress_callback("Dosya okunuyor...")
    df = pd.read_csv(input_file)

    sku_col = check_columns(df, columns_dictionary["sku"], "sku")
    cost_col = check_columns(df, columns_dictionary["cost"], "cost")
    additional_cost_col = check_columns(df, columns_dictionary["additional cost"], "additional_cost")
    bp_strategy_col = check_columns(df, columns_dictionary["bp strategy"], "bp_strategy")
    qd_strategy_col = check_columns(df, columns_dictionary["qd strategy"], "qd_strategy")
    business_pricing_col = check_columns(df, columns_dictionary["business pricing"], "business_pricing")

    if progress_callback:
        progress_callback(f"Veriler Vektörel Olarak Hesaplanıyor (V{version})...")

    # 1. SKU Parçalama ve Fiyat Çıkarma İşlemleri (Vektörel)
    df["Extracted_DC"] = df[sku_col].astype(str).str.split("_").str[0]
    df["Extracted_Price"] = extract_price_vectorized(df[sku_col])
    valid_price_mask = df["Extracted_Price"].notna()

    # 2. Versiyon Bazlı Optimizasyon (Döngü Yok, O(1) İlişkisel Eşleştirme)
    if version == 1:
        # V1 Hesaplaması
        df[additional_cost_col] = df["Extracted_DC"].map(maliyet_dictionary).fillna("#YOK")
        df[cost_col] = "#YOK"
        df.loc[valid_price_mask, cost_col] = df.loc[valid_price_mask, "Extracted_Price"]

    elif version == 2:
        pkg_volume_col = check_columns(df, columns_dictionary["pkg volume"], "pkg_volume")
        pkg_weight_col = check_columns(df, columns_dictionary["pkg weight"], "pkg_weight")

        # Ayarları DataFrame'e çevir ve ilişkisel olarak ana DataFrame ile birleştir (Left Join)
        maliyet_df = pd.DataFrame.from_dict(maliyet_dictionary, orient="index")
        if not maliyet_df.empty:
            df = df.merge(maliyet_df, how="left", left_on="Extracted_DC", right_index=True)
            df[["v2_additional_cost", "v2_equation", "v2_warehouse_fee"]] = df[
                ["v2_additional_cost", "v2_equation", "v2_warehouse_fee"]
            ].fillna(0)
        else:
            df["v2_additional_cost"] = 0
            df["v2_equation"] = 0
            df["v2_warehouse_fee"] = 0

        # pkg hesaplamaları (np.maximum C hızında karşılaştırma yapar)
        vol = pd.to_numeric(df[pkg_volume_col], errors="coerce").fillna(0)
        weight = pd.to_numeric(df[pkg_weight_col], errors="coerce").fillna(0)
        biggest = np.maximum(vol / 139.0, weight)

        eq_ind = df["v2_equation"]
        eq_result = np.zeros(len(df))

        # Equation 1 Hesaplaması
        mask1 = eq_ind == 1
        eq_result = np.where(mask1 & (biggest <= 0.75), 0.18, eq_result)
        eq_result = np.where(mask1 & (biggest > 0.75) & (biggest <= 1.5), 0.22, eq_result)
        eq_result = np.where(mask1 & (biggest > 1.5) & (biggest <= 3.0), 0.27, eq_result)
        eq_result = np.where(mask1 & (biggest > 3.0), 0.37, eq_result)

        # Equation 2 Hesaplaması
        mask2 = eq_ind == 2
        eq_result = np.where(mask2 & (biggest <= 0.75), 0.34, eq_result)
        eq_result = np.where(mask2 & (biggest > 0.75) & (biggest <= 1.5), 0.41, eq_result)
        eq_result = np.where(mask2 & (biggest > 1.5) & (biggest <= 3.0), 0.49, eq_result)
        eq_result = np.where(mask2 & (biggest > 3.0), 0.68, eq_result)

        # V2 Nihai Atamalar
        df[cost_col] = "#YOK"
        df.loc[valid_price_mask, cost_col] = (
            df.loc[valid_price_mask, "Extracted_Price"]
            + eq_result[valid_price_mask]
            + df.loc[valid_price_mask, "v2_warehouse_fee"]
        )
        df[additional_cost_col] = df["v2_additional_cost"]
        
        # Merge sonrası oluşan geçici sütunları temizle
        df.drop(columns=["v2_additional_cost", "v2_equation", "v2_warehouse_fee"], inplace=True)

    # 3. Sabit Değer Atamaları (Döngüden Çıkarıldı)
    df[bp_strategy_col] = "AI"
    df[qd_strategy_col] = "default"
    df[business_pricing_col] = "on"
    
    # Belleği şişirmemek adına işlem gören geçici sütunları atıyoruz
    df.drop(columns=["Extracted_DC", "Extracted_Price"], inplace=True)

    if progress_callback:
        progress_callback("Sonuç dosyası kaydediliyor...")
        
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, os.path.basename(input_file))
    df.to_csv(output_path, index=False)

    return {
        "status": "success",
        "message": f"V{version} İşlemi Vektörel Olarak Başarıyla Tamamlandı!",
        "output_path": output_path,
    }