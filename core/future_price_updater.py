import os
import pandas as pd

def process_future_price(
    path: str, name: str, restock_excel: str, future_excel: str, progress_callback=None
) -> dict:
    if not restock_excel or not os.path.exists(restock_excel):
        raise FileNotFoundError("Hata: Restock dosyası bulunamadı.")
    if not future_excel or not os.path.exists(future_excel):
        raise FileNotFoundError("Hata: Future Price dosyası bulunamadı.")

    if progress_callback:
        progress_callback("Dosyalar okunuyor (Vektörel işlem başlatıldı)...")
        
    restock_df = pd.read_excel(restock_excel)
    future_df = pd.read_excel(future_excel)
    
    if "ASIN" not in restock_df.columns or "ASIN" not in future_df.columns:
        raise ValueError("Hata: İki dosyada da 'ASIN' sütunu bulunmak zorundadır.")
        
    # O(1) arama hızına ulaşmak için dizinleri ASIN olarak ayarla
    r_df = restock_df.set_index("ASIN")
    f_df = future_df.set_index("ASIN")
    
    # 1. TEDARİKÇİLERİ TESPİT ET (Büyük/Küçük Harf Bağımsız)
    r_price_cols = [c for c in r_df.columns if str(c).lower().endswith(" price") and c.lower() != "future price"]
    f_price_cols = [c for c in f_df.columns if str(c).lower().endswith(" price") and c.lower() != "future price"]
    
    def extract_supplier(col_name, suffix=" price"):
        return col_name[:-len(suffix)].strip()
        
    # Future dosyasındaki tedarikçilerin orijinal isimlerini küçük harf (lower) anahtarlarla O(1) Hash Map'e al
    f_suppliers_lower = {extract_supplier(c).lower(): extract_supplier(c) for c in f_price_cols}
        
    # 2. YENİ EKLENECEK SÜTUNLARI HAZIRLA (Sadece Fiyatlar)
    new_data = {}
    
    # Ana Price ve Maliyet (Eğer Future dosyasında varsa)
    if "Price" in f_df.columns:
        new_data["Future Price"] = f_df["Price"]
    if "Maliyet" in f_df.columns:
        new_data["Future Maliyet"] = f_df["Maliyet"]
        
    # Geçerli (Her iki dosyada da olan) tedarikçileri tespit et ve SADECE fiyat verilerini çek
    valid_r_suppliers = []
    for r_col in r_price_cols:
        r_sup = extract_supplier(r_col)
        r_sup_lower = r_sup.lower()
        
        # Yalnızca future listesinde olan tedarikçiler dahil edilir
        if r_sup_lower in f_suppliers_lower:
            f_sup_exact = f_suppliers_lower[r_sup_lower]
            f_col_price = f"{f_sup_exact} price"
            
            if f_col_price in f_df.columns:
                valid_r_suppliers.append(r_sup)
                new_data[f"{r_sup} future price"] = f_df[f_col_price]
                
    # Hesaplanan vektörel sütunları tek bir DataFrame'e dönüştür
    new_cols_df = pd.DataFrame(new_data, index=r_df.index)
    
    # Tüm veriyi bellek parçalanması yaratmadan tek seferde birleştir
    merged_df = pd.concat([r_df, new_cols_df], axis=1)
    
    # 3. SÜTUN SIRALAMASI (İstenilen: İlgili Fiyatın Hemen Sağına Ekleme)
    final_columns = []
    for col in r_df.columns:
        final_columns.append(col)
        
        # Mevcut sütun 'Price' ise yanına hemen 'Future Price' ekle
        if col == "Price" and "Future Price" in new_data:
            final_columns.append("Future Price")
        # Mevcut sütun 'Maliyet' ise yanına hemen 'Future Maliyet' ekle
        elif col == "Maliyet" and "Future Maliyet" in new_data:
            final_columns.append("Future Maliyet")
        else:
            # Mevcut sütun bir tedarikçinin 'price' sütunuysa, yanına 'future price' sütununu ekle
            for r_sup in valid_r_suppliers:
                if col == f"{r_sup} price" and f"{r_sup} future price" in new_data:
                    final_columns.append(f"{r_sup} future price")
                    
    # Sütunları tam olarak istenen sırada yeniden inşa et ve ASIN index'ini geri al
    final_df = merged_df[final_columns].reset_index()
    
    # NaN eksik verileri diske yazarken görsel '#YOK' metnine çevir
    final_df = final_df.fillna("#YOK")
    
    if progress_callback:
        progress_callback("Sonuç dosyası diske kaydediliyor...")
        
    os.makedirs(path, exist_ok=True)
    if not name or name.strip() == "":
        name = "Future_Price_Sonuc"
        
    output_file_path = os.path.join(path, f"{name}.xlsx")
    final_df.to_excel(output_file_path, index=False)
    
    return {
        "status": "success",
        "message": "Future Price işlemi başarıyla tamamlandı!",
        "output_path": path,
    }