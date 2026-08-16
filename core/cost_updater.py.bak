import os
import pandas as pd


def parse_settings(settings_content: str, version: int):
    columns_dictionary = {
        "cost": [],
        "additional cost": [],
        "bp strategy": [],
        "qd strategy": [],
        "business pricing": [],
        "sku": [],
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
                            "additional cost": values[0],
                            "equation": values[1],
                            "warehouse fee": values[2],
                        }

    return columns_dictionary, maliyet_dictionary


def equation(code, value):
    code = int(code)
    if code == 1:
        if value <= 0.75:
            return 0.18
        elif value <= 1.5:
            return 0.22
        elif value <= 3:
            return 0.27
        else:
            return 0.37
    elif code == 2:
        if value <= 0.75:
            return 0.34
        elif value <= 1.5:
            return 0.41
        elif value <= 3:
            return 0.49
        else:
            return 0.68
    return 0


def check_columns(df, liste, isim):
    for col in liste:
        if col in df.columns:
            return col
    raise ValueError(
        f"Eksik Sütun Hatası: Yüklenen CSV dosyasında '{isim}' için beklenen sütunlardan hiçbiri bulunamadı. Beklenen sütun adları: {liste}. Lütfen dosyayı düzeltip tekrar başlatın."
    )

def process_costupdater(
        input_file: str, output_folder: str, settings_content: str, version: int, progress_callback=None
) -> dict:
    if not input_file or not os.path.exists(input_file):
        raise FileNotFoundError("Hata: İşlenecek CSV dosyası bulunamadı.")

    # Ortak ayrıştırma
    columns_dictionary, maliyet_dictionary = parse_settings(settings_content, version=version)

    if progress_callback:
        progress_callback("Dosya okunuyor...")
    df = pd.read_csv(input_file)

    # Ortak Sütun Kontrolleri
    sku_col = check_columns(df, columns_dictionary["sku"], "sku")
    cost_col = check_columns(df, columns_dictionary["cost"], "cost")
    additional_cost_col = check_columns(df, columns_dictionary["additional cost"], "additional_cost")
    bp_strategy_col = check_columns(df, columns_dictionary["bp strategy"], "bp_strategy")
    qd_strategy_col = check_columns(df, columns_dictionary["qd strategy"], "qd_strategy")
    business_pricing_col = check_columns(df, columns_dictionary["business pricing"], "business_pricing")

    # Sadece V2 için gereken sütunlar
    if version == 2:
        pkg_volume_col = check_columns(df, columns_dictionary["pkg volume"], "pkg_volume")
        pkg_weight_col = check_columns(df, columns_dictionary["pkg weight"], "pkg_weight")
        pkg_volume = df[pkg_volume_col].tolist()
        pkg_weight = df[pkg_weight_col].tolist()

    sku = df[sku_col].tolist()
    cost = df[cost_col].tolist()
    additional_cost = df[additional_cost_col].tolist()
    bp_strategy = df[bp_strategy_col].tolist()
    qd_strategy = df[qd_strategy_col].tolist()
    business_pricing = df[business_pricing_col].tolist()

    if progress_callback:
        progress_callback(f"Veriler hesaplanıyor (V{version})...")

    # Ana Döngü
    for a, i in enumerate(sku):
        split_liste = str(i).split("_")
        dc = split_liste[0]
        price = ""

        for z in split_liste[1:]:
            if "." in str(z) or "," in str(z):
                z = str(z).replace(",", ".")
                try:
                    price = float(z)
                except ValueError:
                    price = ""

        # VERSİYON BAZLI HESAPLAMA İZOLASYONU
        if version == 1:
            maliyet = maliyet_dictionary.get(dc, "#YOK")
            if maliyet == "#YOK" and progress_callback:
                progress_callback(f"Uyarı: '{i}' için ayarlar dosyasında additional cost değeri bulunamadı.")

            cost[a] = price if price != "" else "#YOK"
            additional_cost[a] = maliyet

        elif version == 2:
            try:
                dc_data = maliyet_dictionary[dc]
                maliyet = dc_data["additional cost"]
                equation_indicator = dc_data["equation"]
                warehouse_fee = dc_data["warehouse fee"]
            except KeyError:
                if progress_callback:
                    progress_callback(f"Uyarı: '{i}' için ayarlar dosyasında eksik veri.")
                maliyet, equation_indicator, warehouse_fee = 0, 0, 0

            try:
                vol = float(pkg_volume[a])
                weight = float(pkg_weight[a])
                biggest = max(float(vol / 139), weight)
            except (ValueError, IndexError):
                biggest = 0

            if price != "":
                cost[a] = float(price) + float(equation(int(equation_indicator), biggest)) + float(warehouse_fee)
            else:
                cost[a] = price

            additional_cost[a] = maliyet

        # Ortak atamalar
        bp_strategy[a] = "AI"
        qd_strategy[a] = "default"
        business_pricing[a] = "on"

    # Ortak Kaydetme İşlemleri
    df[cost_col] = cost
    df[additional_cost_col] = additional_cost
    df[bp_strategy_col] = bp_strategy
    df[qd_strategy_col] = qd_strategy
    df[business_pricing_col] = business_pricing

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, os.path.basename(input_file))

    if progress_callback:
        progress_callback("Sonuç dosyası kaydediliyor...")
    df.to_csv(output_path, index=False)

    return {
        "status": "success",
        "message": f"V{version} İşlemi başarıyla tamamlandı!",
        "output_path": output_path,
    }