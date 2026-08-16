import os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np


def find_column(df, possible_columns, error_msg):
    for column in possible_columns:
        if column in df.columns:
            return column
    raise ValueError(f"Eksik Sütun Hatası: {error_msg}")


def process_export(path, row_file, export_files, columns_dict, dataframe_dictionary):
    row_code = os.path.basename(row_file).split("-")[0]
    row_df = dataframe_dictionary[row_file].copy()

    colrow = find_column(
        row_df,
        columns_dict["upc"],
        f"{row_file} ham dosyası için UPC sütunu bulunamadı.",
    )

    export_file = next(
        (f for f in export_files if os.path.basename(f).split("-")[0] == row_code), None
    )

    if not export_file:
        raise ValueError(f"Eşleşen export dosyası bulunamadı: {row_code}")

    export_df = pd.read_excel(export_file, engine="openpyxl")
    colexp = find_column(
        export_df,
        columns_dict["upc"],
        f"{export_file} export dosyası için UPC sütunu bulunamadı.",
    )
    qtycol = find_column(
        export_df,
        columns_dict["Quantity on hand"],
        f"{export_file} export dosyası için Quantity sütunu bulunamadı.",
    )

    qty_series = export_df.drop_duplicates(subset=[colexp]).set_index(colexp)[qtycol]
    row_df = row_df[row_df[colrow].isin(qty_series.index)].copy()

    price_sutun = find_column(
        row_df,
        columns_dict["price"],
        f"{row_file} ham dosyası için Price sütunu bulunamadı.",
    )
    quantity_mapped = row_df[colrow].map(qty_series)

    try:
        price_index = row_df.columns.get_loc(price_sutun)
        row_df.insert(price_index + 1, "Qty on Hand", quantity_mapped)
    except KeyError:
        insert_idx = min(21, row_df.shape[1])
        row_df.insert(insert_idx, "Qty on Hand", quantity_mapped)

    save_path = os.path.join(path, "sonuclar", os.path.basename(row_file))
    
    # Sadece Diske yazılırken görsellik (#YOK) uygulanır
    row_df.fillna({"Qty on Hand": "#YOK"}).to_excel(
        save_path, index=False, sheet_name="export sonuc", engine="openpyxl"
    )
    
    return row_df


def process_restock_logic(
    path,
    row_files,
    export_files,
    restock_files,
    islem,
    save_name,
    settings_dict,
    progress_callback=None,
):
    if not row_files:
        raise ValueError("Ham dosyalar (Row files) eksik.")

    os.makedirs(os.path.join(path, "sonuclar"), exist_ok=True)
    columns_dict = settings_dict.get("columns", {})
    maliyet_dict = settings_dict.get("deposits", {})
    
    dataframe_dictionary = {}

    # 1. DOSYALARI OKUMA (paralel - eski uygulamadaki ThreadPool davranışı)
    def _read_row_file(file):
        return file, pd.read_excel(file, engine="openpyxl")

    with ThreadPoolExecutor() as pool:
        for i, (file, df) in enumerate(pool.map(_read_row_file, row_files)):
            if progress_callback:
                progress_callback(
                    f"Okunuyor ({i+1}/{len(row_files)}): {os.path.basename(file)}", 10
                )
            dataframe_dictionary[file] = df

    # 2. EXPORT
    if islem.get("export") == 1:
        if not export_files:
            raise ValueError("Export seçildi ancak export dosyaları eksik.")
        for i, row_file in enumerate(row_files):
            if progress_callback:
                progress_callback(
                    f"Export işleniyor ({i+1}/{len(row_files)}): {os.path.basename(row_file)}",
                    30,
                )
            dataframe_dictionary[row_file] = process_export(
                path, row_file, export_files, columns_dict, dataframe_dictionary
            )

    # 3. BİRBİRİNDEN DÜŞME TESPİTİ (Vektörel Optimizasyon)
    if progress_callback:
        progress_callback("UPC çakışmaları ve en düşük fiyatlar vektörel olarak hesaplanıyor...", 50)

    # Adım 3.1: Tüm dosyaların UPC ve Price verilerini tek bir havuza topla
    all_items = []
    for i, file in enumerate(row_files):
        df = dataframe_dictionary[file]
        upc_col = find_column(
            df,
            columns_dict["upc"],
            f"{file} için UPC bulunamadı.",
        )
        price_col = find_column(
            df,
            columns_dict["price"],
            f"{file} için Price bulunamadı.",
        )

        # İlgili sütunları al ve standartlaştır
        temp_df = df[[upc_col, price_col]].copy()
        temp_df.columns = ["UPC", "Price"]
        temp_df["File"] = file
        temp_df["Priority"] = i  # Eşitlik durumunda ilk dosya kazanması için
        all_items.append(temp_df)

    # Tüm dosyaları tek bir Pandas yapısında birleştir
    combined_df = pd.concat(all_items, ignore_index=True)

    # Fiyat sütununu sayısal değere zorla (String sızmışsa NaN yapar, çökmeyi engeller)
    combined_df["Price"] = pd.to_numeric(combined_df["Price"], errors="coerce")

    # Adım 3.2: O(1) Hızında Çakışma Çözümü
    # UPC'ye göre grupla. Fiyatı artan, önceliği artan şekilde sırala.
    # Böylece her UPC'nin en düşük fiyatlısı (ve eşitlikte ilk dosyası) en üste çıkar.
    combined_df = combined_df.sort_values(by=["UPC", "Price", "Priority"])

    # En üstteki (kazanan) UPC'leri tut, tekrarları at.
    winners_df = combined_df.drop_duplicates(subset=["UPC"], keep="first")

    # 4. Adımda kullanmak üzere hangi dosyada hangi UPC'lerin KALACAĞINI bir O(1) Hash Map'e (Set) al
    keep_upc = {file: set() for file in row_files}
    for file, group in winners_df.groupby("File"):
        keep_upc[file] = set(group["UPC"])


    # 4. BİRBİRİNDEN DÜŞME UYGULAMA
    row_dataframe_dictionary = {}
    for i, file in enumerate(row_files):
        if progress_callback:
            progress_callback(f"UPC'ler siliniyor: {os.path.basename(file)}", 60)

        df = dataframe_dictionary[file]
        upc_col = find_column(
            df, columns_dict["upc"], f"{file} için UPC bulunamadı."
        )

        # MANTIK DÜZELTİLDİ: "Silinecekleri bul ve çıkar" yerine doğrudan "Kazananları filtrele"
        df_filtered = df[df[upc_col].isin(keep_upc[file])]

        save_path = os.path.join(path, "sonuclar", os.path.basename(file))
        mode = "a" if islem.get("export") == 1 and os.path.exists(save_path) else "w"

        if mode == "a":
            with pd.ExcelWriter(save_path, engine="openpyxl", mode="a") as writer:
                df_filtered.to_excel(writer, sheet_name="dusulmus liste", index=False)
        else:
            df_filtered.to_excel(save_path, sheet_name="dusulmus liste", index=False)

        # Filtrelenmiş DataFrame bellekte korunuyor (5. adım için)
        row_dataframe_dictionary[file] = df_filtered

    # 5. RESTOCK (Tamamen Vektörize Edilmiş Mimari)
    if islem.get("restock") == 1:
        if not restock_files:
            raise ValueError("Restock (Ana) excel dosyası eksik.")
        if progress_callback:
            progress_callback("Restock birleştirmesi vektörel olarak yapılıyor...", 70)

        main_excel = restock_files[0]
        main_excel_df = pd.read_excel(main_excel, engine="openpyxl")
        
        main_upc_col = find_column(main_excel_df, columns_dict["upc"], f"{main_excel} için UPC bulunamadı.")
        main_pk_col = find_column(main_excel_df, columns_dict["pk"], f"{main_excel} için PK bulunamadı.")

        # Adım 5.1: Bütün satır (Row) ve dışa aktarım (Export) verilerini tek bir ilişkisel tabloda topla
        dfs_to_concat = []
        supplier_order = [] # Sütunları orjinal sırasıyla eklemek için
        
        for i, file in enumerate(row_files):
            filename = os.path.basename(file).split("-")[0]
            supplier_order.append(filename)
            
            # Export DataFrame Sütunları
            exp_df = dataframe_dictionary[file]
            e_upc = find_column(exp_df, columns_dict["upc"], "UPC Yok")
            e_price = find_column(exp_df, columns_dict["price"], "Price Yok")
            e_brand = find_column(exp_df, columns_dict["brand"], "Brand Yok")
            e_qty = find_column(exp_df, columns_dict["Quantity on hand"], "Quantity Yok")
            
            exp_subset = exp_df[[e_upc, e_price, e_qty, e_brand]].copy()
            exp_subset.columns = ["UPC", "Price", "E_Qty", "Brand"]
            exp_subset["Price"] = pd.to_numeric(exp_subset["Price"], errors="coerce")
            
            # Row DataFrame Sütunları
            row_df = row_dataframe_dictionary[file]
            r_upc = find_column(row_df, columns_dict["upc"], "UPC Yok")
            r_case = find_column(row_df, columns_dict["case"], "Case Yok")
            r_qty = find_column(row_df, columns_dict["Quantity on hand"], "Quantity Yok")
            
            row_subset = row_df[[r_upc, r_case, r_qty]].copy()
            row_subset.columns = ["UPC", "Case", "R_Qty"]
            
            # O(1) İlişkisel Birleştirme (Inner Join)
            merged = pd.merge(exp_subset, row_subset, on="UPC", how="inner")
            merged["Supplier"] = filename
            merged["Priority"] = i
            
            dfs_to_concat.append(merged)

        # Tüm veriyi Pandas hafızasında birleştir
        all_supplier_data = pd.concat(dfs_to_concat, ignore_index=True)
        
        # Adım 5.2: Her UPC için En Düşük Fiyatlı (Kazanan) Tedarikçiyi Bul
        all_supplier_data = all_supplier_data.sort_values(by=["UPC", "Price", "Priority"])
        winners_df = all_supplier_data.drop_duplicates(subset=["UPC"], keep="first").set_index("UPC")
        
        # Adım 5.3: Tedarikçilere Özel Fiyat ve Miktarları Pivot Tabloya Çevir
        unique_for_pivot = all_supplier_data.drop_duplicates(subset=["UPC", "Supplier"])
        pivot_price = unique_for_pivot.set_index(["UPC", "Supplier"])["Price"].unstack()
        pivot_qty = unique_for_pivot.set_index(["UPC", "Supplier"])["E_Qty"].unstack()

        if progress_callback:
            progress_callback("Veriler Ana Excel'e entegre ediliyor...", 80)
            
        # Adım 5.4: Ana DataFrame'e Verileri Haritalama (Mapping)
        main_upcs = main_excel_df[main_upc_col]
        
        # Yeni eklenecek sütunları parçalanmayı (fragmentation) önlemek için sözlükte topla
        new_columns = {}
        
        new_columns["Brand"] = main_upcs.map(winners_df["Brand"])
        new_columns["Price"] = main_upcs.map(winners_df["Price"])
        
        # Maliyet Hesaplaması (Döngüsüz, Tamamen Vektörel)
        winning_suppliers = main_upcs.map(winners_df["Supplier"])
        
        # PK sütununu temizle ve sayısala çevir
        pk_numeric = main_excel_df[main_pk_col].astype(str).str.replace("PK", "").apply(pd.to_numeric, errors="coerce")
        sup_costs = winning_suppliers.map(maliyet_dict).fillna(0.0)
        
        maliyet_calc = (pk_numeric * new_columns["Price"]) + sup_costs
        new_columns["Maliyet"] = maliyet_calc.fillna(new_columns["Price"])
        
        new_columns["Case"] = main_upcs.map(winners_df["Case"])
        
        # Tedarikçi Özel Fiyatları
        for sup in supplier_order:
            col_name = f"{sup} price"
            new_columns[col_name] = main_upcs.map(pivot_price[sup]) if sup in pivot_price.columns else np.nan
            
        new_columns["Qty on Hand"] = main_upcs.map(winners_df["R_Qty"])
        
        # Tedarikçi Özel Miktarları
        for sup in supplier_order:
            col_name = f"{sup} quantity"
            new_columns[col_name] = main_upcs.map(pivot_qty[sup]) if sup in pivot_qty.columns else np.nan
            
        new_columns["suplier"] = winning_suppliers
        
        # Adım 5.5: Yeni Sütunları Tek Seferde Birleştir ve Temizle
        new_cols_df = pd.DataFrame(new_columns, index=main_excel_df.index)
        final_df = pd.concat([main_excel_df, new_cols_df], axis=1)
        
        if progress_callback:
            progress_callback("Restock dosyası kaydediliyor...", 90)
            
        # Price verisi NaN olanları (eski kodda mantıksızca "#YOK" basılanları) DataFrame'den uçur
        final_df = final_df.dropna(subset=["Price"])
        
        # NaN olarak hesaplanan ve bellekte sayısal kalan verileri sadece diske yazarken görsel "#YOK"a çevir
        final_df = final_df.fillna("#YOK")
        
        os.makedirs(os.path.join(path, "restock"), exist_ok=True)
        final_df.to_excel(
            os.path.join(path, "restock", f"{save_name}.xlsx"),
            index=False,
            sheet_name="restock",
            engine="openpyxl",
        )

    if progress_callback:
        progress_callback("Tüm işlemler başarıyla tamamlandı!", 100)
    return {"status": "success", "output_path": path}
