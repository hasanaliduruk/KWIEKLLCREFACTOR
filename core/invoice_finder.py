import os
import shutil
import pandas as pd
import numpy as np


def process_invoice_finder(
    source_excel: str,
    all_invoices_excel: str,
    invoice_pdf_folder: str,
    output_folder: str,
    user_input_date: str,
    progress_callback=None,
) -> dict:
    if not all([os.path.exists(p) for p in [source_excel, all_invoices_excel, invoice_pdf_folder]]):
        raise FileNotFoundError("Hata: Gerekli dosya veya klasörlerden biri bulunamadı.")

    user_date = pd.to_datetime(user_input_date, format="%d.%m.%Y", errors="coerce")
    if pd.isna(user_date):
        raise ValueError("Hatalı tarih formatı. Lütfen GG.AA.YYYY formatında giriniz.")

    # 1. KAYNAK EXCEL PARÇALAMA (Vektörel Veri Çerçevesi İnşası)
    if progress_callback: progress_callback("Kaynak excel dosyası işleniyor...")
    df_raw = pd.read_excel(source_excel, header=None)[0].astype(str).tolist()
    
    parsed_data = []
    curr_asin = None
    for i in range(len(df_raw)):
        if df_raw[i].count("_") >= 3:
            curr_asin = df_raw[i]
        elif "FNSKU" in df_raw[i] and curr_asin:
            qty_str = df_raw[i + 1] if i + 1 < len(df_raw) else "0"
            parsed_data.append({"SKU": curr_asin, "FNSKU": df_raw[i], "QtyRaw": qty_str})
            curr_asin = None

    if not parsed_data:
        raise ValueError("Kaynak excel dosyasından hiçbir ASIN verisi çıkarılamadı.")

    df_src = pd.DataFrame(parsed_data)

    # Mantık Düzeltildi: İç içe string manipülasyonu yerine vektörel koşullar
    df_src["CleanQty"] = np.where(
        df_src["QtyRaw"].str.contains("-"), 
        df_src["FNSKU"], 
        df_src["QtyRaw"].str.split("+").str[0]
    )
    df_src["CleanQty"] = pd.to_numeric(df_src["CleanQty"], errors="coerce").fillna(0).astype(int)

    sku_split = df_src["SKU"].str.split("_")
    df_src["UPC"] = pd.to_numeric(sku_split.str[1], errors="coerce")
    df_src["PK"] = sku_split.str[2].astype(str).str.replace("PK", "", regex=False)
    df_src["PK"] = pd.to_numeric(df_src["PK"], errors="coerce").fillna(1).astype(int)
    
    df_src["amazonshipquantity"] = df_src["CleanQty"] * df_src["PK"]

    # Aynı UPC'ye sahip ASIN'leri grupla ve hedefleri belirle
    upc_targets = df_src.groupby("UPC", as_index=False)["amazonshipquantity"].sum()
    upc_targets.rename(columns={"amazonshipquantity": "TargetQty"}, inplace=True)

    # 2. ALL INVOICES EXCEL İŞLEME (O(1) İlişkisel Algoritma)
    if progress_callback: progress_callback("All Invoices excel dosyası Vektörel olarak işleniyor...")
    df_all = pd.read_excel(all_invoices_excel)
    df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")
    df_all["Upc"] = pd.to_numeric(df_all["Upc"], errors="coerce")
    df_all["ShipQuantity"] = pd.to_numeric(df_all["ShipQuantity"], errors="coerce").fillna(0).astype(int)

    # Sadece belirlenen tarihten önceki ve bizde hedefi olan UPC'leri filtrele
    valid_invs = df_all[(df_all["Date"] <= user_date) & (df_all["Upc"].isin(upc_targets["UPC"]))].copy()
    
    # Tarihe göre azalan (en yeni fatura en üstte) sırala
    valid_invs = valid_invs.sort_values(by=["Upc", "Date"], ascending=[True, False])

    # 3. KÜMÜLATİF TOPLAM (Greedy While Döngüsü Yerine C Tabanlı CumSum)
    valid_invs = valid_invs.merge(upc_targets, left_on="Upc", right_on="UPC", how="inner")
    valid_invs["CumQty"] = valid_invs.groupby("Upc")["ShipQuantity"].cumsum()
    valid_invs["PrevCumQty"] = valid_invs["CumQty"] - valid_invs["ShipQuantity"]
    
    # Hedef Miktarı doldurana kadar olan faturaları seç (PrevCumQty < TargetQty kuralı)
    selected_invs = valid_invs[valid_invs["PrevCumQty"] < valid_invs["TargetQty"]].copy()

    # Çıktı formatlaması için verileri UPC bazında string olarak birleştir
    selected_invs["FormattedDate"] = selected_invs["Date"].dt.strftime("%d-%m-%Y")
    
    agg_invs = selected_invs.groupby("Upc").agg(
        InvSum=("ShipQuantity", "sum"),
        InvNums=("InvoiceNumber", lambda x: ", ".join(x.astype(str).unique())),
        ItemNums=("ShipItem", lambda x: ", ".join(x.astype(float).astype(int).astype(str))),
        Dates=("FormattedDate", lambda x: ", ".join(x)),
        EachQty=("ShipQuantity", lambda x: ", ".join(x.astype(str)))
    ).reset_index()

    # 4. FİNAL SONUÇLARININ HAZIRLANMASI
    df_final = df_src.merge(upc_targets, on="UPC", how="left").merge(agg_invs, left_on="UPC", right_on="Upc", how="left")
    
    df_final["invoice quantity"] = df_final["InvSum"].fillna(0).astype(int)
    df_final["Fark"] = df_final["invoice quantity"] - df_final["TargetQty"]
    df_final["Fark"] = df_final["Fark"].apply(lambda x: f"+{int(x)}" if pd.notna(x) and x > 0 else (str(int(x)) if pd.notna(x) else ""))
    df_final["Yapildi/Yapilmadi"] = np.where(df_final["InvNums"].notna() & (df_final["InvNums"] != ""), "Yapildi", "Yapilmadi")

    # İstenen sütun isimlerine haritalama
    output_df = pd.DataFrame({
        "SKU": df_final["SKU"],
        "upc": df_final["UPC"].astype(str).str.replace(".0", "", regex=False),
        "pk": df_final["SKU"].str.split("_").str[2],
        "amazonshipquantity": df_final["amazonshipquantity"],
        "invoice quantity": df_final["invoice quantity"].replace(0, ""),
        "item number": df_final["ItemNums"].fillna(""),
        "invoice number": df_final["InvNums"].fillna(""),
        "invoice each": df_final["EachQty"].fillna(""),
        "invoice date": df_final["Dates"].fillna(""),
        "Yapildi/Yapilmadi": df_final["Yapildi/Yapilmadi"],
        "Fark": df_final["Fark"]
    })

    # 5. DİSK OKUMA OPTİMİZASYONU (I/O Thrashing Engellendi)
    if progress_callback: progress_callback("Fatura PDF'leri O(1) indekslemesi ile kopyalanıyor...")
    
    os.makedirs(output_folder, exist_ok=True)
    all_pdfs = os.listdir(invoice_pdf_folder)
    needed_inv_strs = set(selected_invs["InvoiceNumber"].astype(str))
    
    # Disk dizini yalnızca BİR KEZ taranır
    for pdf_file in all_pdfs:
        if any(inv in pdf_file for inv in needed_inv_strs):
            shutil.copy2(os.path.join(invoice_pdf_folder, pdf_file), os.path.join(output_folder, pdf_file))

    if progress_callback: progress_callback("Sonuç excel dosyası kaydediliyor...")
    output_df.to_excel(os.path.join(output_folder, "sonexcel.xlsx"), index=False)

    return {
        "status": "success",
        "message": "Invoice Finder İşlemi başarıyla tamamlandı!",
        "output_path": output_folder,
    }


def process_invoice_finder_upc(
    all_invoices_excel: str,
    invoice_pdf_folder: str,
    output_folder: str,
    upcs_str: str,
    months_str: str,
    progress_callback=None,
) -> dict:
    if not all([os.path.exists(p) for p in [all_invoices_excel, invoice_pdf_folder]]):
        raise FileNotFoundError("Hata: Gerekli dosya veya klasörlerden biri bulunamadı.")

    if progress_callback: progress_callback("ALL INVOICES excel dosyası okunuyor...")
    df = pd.read_excel(all_invoices_excel)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Upc"] = pd.to_numeric(df["Upc"], errors="coerce")

    try:
        int_month = int(months_str)
    except ValueError:
        raise ValueError("Geçersiz ay değeri. Lütfen tam sayı giriniz.")

    # Hedef UPC'leri vektörel listeye dönüştür
    split_upc = [float(u.strip()) for u in upcs_str.split(",") if u.strip() and u.strip().replace(".", "", 1).isdigit()]
    if not split_upc:
        raise ValueError("Geçerli bir UPC değeri girilmedi.")

    # Veriyi izole et
    valid_invoices = df[df["Upc"].isin(split_upc)].copy()

    if int_month != 0:
        before_months = pd.Timestamp.now() - pd.DateOffset(months=int_month)
        valid_invoices = valid_invoices[valid_invoices["Date"] > before_months]
        if progress_callback: progress_callback(f"{int_month} ay öncesine kadar olan faturalar filtrelendi...")

    needed_invs = set(valid_invoices["InvoiceNumber"].astype(str))
    if not needed_invs:
        raise ValueError("Belirtilen kriterlere uygun hiçbir fatura verisi bulunamadı.")

    # Disk okuma optimizasyonu: İçi içe O(N^2) dizin taraması önlendi
    found_any = False
    all_pdfs = os.listdir(invoice_pdf_folder)
    
    for pdf_file in all_pdfs:
        matching_invs = [inv for inv in needed_invs if inv in pdf_file]
        for inv in matching_invs:
            found_any = True
            # Faturanın ait olduğu UPC'leri tespit et ve ilgili klasörlere dağıt
            upcs_for_inv = valid_invoices.loc[valid_invoices["InvoiceNumber"].astype(str) == inv, "Upc"].unique()
            for u in upcs_for_inv:
                target_dir = os.path.join(output_folder, str(int(u))) if len(split_upc) > 1 else output_folder
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(os.path.join(invoice_pdf_folder, pdf_file), os.path.join(target_dir, pdf_file))

    if not found_any:
        raise ValueError("Belirtilen kriterlere uygun hiçbir fatura PDF'i bulunamadı.")

    return {
        "status": "success",
        "message": "Faturalar vektörel hızda başarıyla bulundu ve kopyalandı!",
        "output_path": output_folder,
    }