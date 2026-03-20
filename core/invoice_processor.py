import os
import pandas as pd

def parse_invoice_settings(settings_content: str):
    columns_dict = {'remove': [], 'shipquantity': [], 'date': []}
    lines = [line.strip() for line in settings_content.split('\n') if line.strip()]
    for line in lines:
        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip().lower()
            if key in columns_dict:
                columns_dict[key] = [v.strip() for v in val.split(',')]
    return columns_dict

def find_column(df, possible_columns, error_context):
    for col in possible_columns:
        if col in df.columns:
            return col
    raise ValueError(f"Eksik Sütun Hatası: '{error_context}' dosyasında beklenen sütunlardan hiçbiri bulunamadı. Beklenenler: {possible_columns}. Lütfen dosyayı veya ayarları düzeltin.")

def process_invoice(input_files: list, output_folder: str, settings_content: str, delzero: int, progress_callback=None) -> dict:
    if not input_files:
        raise FileNotFoundError("Hata: İşlenecek CSV dosyası bulunamadı.")

    columns_dict = parse_invoice_settings(settings_content)
    dataframes = []

    for file in input_files:
        if not os.path.exists(file):
            continue
        if progress_callback: progress_callback(f"Okunuyor: {os.path.basename(file)}")
        df = pd.read_csv(file)
        
        # Sütunları doğrula (Eksikse anında ValueError fırlatır, sistemi dondurmaz)
        find_column(df, columns_dict['shipquantity'], os.path.basename(file))
        find_column(df, columns_dict['date'], os.path.basename(file))
        
        dataframes.append(df)

    if not dataframes:
        raise ValueError("Hata: Birleştirilecek geçerli veri bulunamadı.")

    if progress_callback: progress_callback("Veriler birleştiriliyor...")
    df_merged = pd.concat(dataframes, ignore_index=True)

    if progress_callback: progress_callback("Gereksiz sütunlar temizleniyor...")
    df_merged.drop(columns=columns_dict['remove'], axis=1, inplace=True, errors='ignore')

    if progress_callback: progress_callback("Miktarlar kontrol ediliyor...")
    sq_col = find_column(df_merged, columns_dict['shipquantity'], 'Birleştirilmiş Veri')
    if delzero != 0:
        df_merged = df_merged[df_merged[sq_col] != 0]

    if progress_callback: progress_callback("Tarihler formatlanıyor...")
    date_col = find_column(df_merged, columns_dict['date'], 'Birleştirilmiş Veri')
    
    new_date_list = []
    for date in df_merged[date_col].tolist():
        date_str = str(date).strip()
        try:
            if '/' in date_str:
                parts = date_str.split('/')
                new_date_list.append(f"{parts[1]}/{parts[0]}/{parts[2]}")
            elif ',' in date_str:
                parts = date_str.split(',')
                new_date_list.append(f"{parts[1]}/{parts[0]}/{parts[2]}")
            elif '-' in date_str:
                parts = date_str.split('-')
                new_date_list.append(f"{parts[1]}/{parts[0]}/{parts[2]}")
            else:
                new_date_list.append('#HATA')
        except IndexError:
            new_date_list.append('#HATA')

    df_merged[date_col] = new_date_list

    if progress_callback: progress_callback("Sayı formatları (nokta/virgül) dönüştürülüyor...")
    df_merged = df_merged.map(lambda x: str(x).replace('.', ',') if isinstance(x, (str, float)) and x != 0 and x != 0.0 else x)

    os.makedirs(os.path.join(output_folder, 'invoice_sonuc_excel'), exist_ok=True)
    output_path = os.path.join(output_folder, 'invoice_sonuc_excel', 'toplu.xlsx')

    if progress_callback: progress_callback("Sonuç Excel dosyasına kaydediliyor...")
    df_merged.to_excel(output_path, index=False)

    return {"status": "success", "message": "İşlem başarıyla tamamlandı!", "output_path": output_path}