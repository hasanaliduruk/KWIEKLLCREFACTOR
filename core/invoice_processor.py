import os
import pandas as pd


def find_column(df, possible_columns, error_context):
    for col in possible_columns:
        if col in df.columns:
            return col
    raise ValueError(
        f"Eksik Sütun Hatası: '{error_context}' dosyasında beklenen sütunlardan hiçbiri bulunamadı. "
        f"Beklenenler: {possible_columns}. Lütfen dosyayı veya ayarları düzeltin."
    )


def process_invoice(
    input_files: list,
    output_folder: str,
    settings_dict: dict,
    delzero: int,
    progress_callback=None,
) -> dict:
    if not input_files:
        raise FileNotFoundError("Hata: İşlenecek CSV dosyası bulunamadı.")

    columns_dict = settings_dict.get("columns", {})
    dataframes = []

    for file in input_files:
        if not os.path.exists(file):
            continue
        if progress_callback:
            progress_callback(f"Okunuyor: {os.path.basename(file)}")
            
        df = pd.read_csv(file)

        # Sütunları doğrula
        find_column(df, columns_dict["shipquantity"], os.path.basename(file))
        find_column(df, columns_dict["date"], os.path.basename(file))

        dataframes.append(df)

    if not dataframes:
        raise ValueError("Hata: Birleştirilecek geçerli veri bulunamadı.")

    if progress_callback:
        progress_callback("Veriler O(1) hızında birleştiriliyor...")
    df_merged = pd.concat(dataframes, ignore_index=True)

    if progress_callback:
        progress_callback("Gereksiz sütunlar temizleniyor...")
    df_merged.drop(columns=columns_dict["remove"], inplace=True, errors="ignore")

    if progress_callback:
        progress_callback("Miktarlar kontrol ediliyor...")
    sq_col = find_column(df_merged, columns_dict["shipquantity"], "Birleştirilmiş Veri")
    
    # Sütunun sayısal olduğundan emin ol (String sızıntılarını engelle)
    df_merged[sq_col] = pd.to_numeric(df_merged[sq_col], errors="coerce").fillna(0)
    
    if delzero != 0:
        df_merged = df_merged[df_merged[sq_col] != 0]

    if progress_callback:
        progress_callback("Tarihler vektörel olarak formatlanıyor...")
    date_col = find_column(df_merged, columns_dict["date"], "Birleştirilmiş Veri")

    # Tüm regex ve datetime dönüşümleri saf Pandas vektörizasyonu ile yapıldı
    clean_dates = df_merged[date_col].astype(str).str.replace(r'[,-]', '/', regex=True)
    df_merged[date_col] = pd.to_datetime(clean_dates, format='mixed', errors='coerce').dt.strftime('%d.%m.%Y').fillna("#HATA")

    output_path = os.path.join(output_folder, "toplu.xlsx")

    if progress_callback:
        progress_callback("Sonuç Excel dosyasına kaydediliyor...")
    df_merged.to_excel(output_path, index=False)

    return {
        "status": "success",
        "message": "İşlem vektörel hızda başarıyla tamamlandı!",
        "output_path": output_folder,
    }