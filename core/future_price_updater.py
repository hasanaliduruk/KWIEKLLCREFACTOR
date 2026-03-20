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
        progress_callback("Restock dosyası okunuyor...")
    restock_df = pd.read_excel(restock_excel)
    restock_dictionary = {}

    # Tüm "price" içeren sütunları bulma
    price_columns_list = [col for col in restock_df.columns if "price" in col.lower()]
    all_asins = restock_df["ASIN"].tolist()

    for i, asin in enumerate(all_asins):
        restock_dictionary[asin] = {
            "Price": (
                restock_df["Price"][i] if "Price" in restock_df.columns else "#YOK"
            ),
            "Maliyet": (
                restock_df["Maliyet"][i] if "Maliyet" in restock_df.columns else "#YOK"
            ),
        }
        for col_name in price_columns_list:
            restock_dictionary[asin][col_name] = restock_df[col_name][i]

    if progress_callback:
        progress_callback("Future Price dosyası okunuyor ve veriler işleniyor...")
    future_df = pd.read_excel(future_excel)
    future_dictionary = {}
    future_price_columns = [col for col in future_df.columns if "price" in col.lower()]
    future_asins = future_df["ASIN"].tolist()

    for i, asin in enumerate(future_asins):
        future_dictionary[asin] = {
            "Price": future_df["Price"][i] if "Price" in future_df.columns else "#YOK",
            "Maliyet": (
                future_df["Maliyet"][i] if "Maliyet" in future_df.columns else "#YOK"
            ),
        }
        for col_name in future_price_columns:
            future_dictionary[asin][col_name] = future_df[col_name][i]

    for asin in restock_dictionary.keys():
        if asin in future_dictionary:
            restock_dictionary[asin]["Future Price"] = future_dictionary[asin]["Price"]
            restock_dictionary[asin]["Future Maliyet"] = future_dictionary[asin][
                "Maliyet"
            ]
            for col_name in price_columns_list:
                future_name = col_name.lower().replace("price", "future price")
                restock_dictionary[asin][future_name] = future_dictionary[asin].get(
                    col_name, "#YOK"
                )
        else:
            restock_dictionary[asin]["Future Price"] = "#YOK"
            restock_dictionary[asin]["Future Maliyet"] = "#YOK"
            for col_name in price_columns_list:
                future_name = col_name.lower().replace("price", "future price")
                restock_dictionary[asin][future_name] = "#YOK"

    future_price_list = []
    future_maliyet_list = []
    write_dict = {
        col.lower().replace("price", "future price"): [] for col in price_columns_list
    }

    for i, asin in enumerate(restock_df["ASIN"].tolist()):
        future_price_list.append(restock_dictionary[asin]["Future Price"])
        future_maliyet_list.append(restock_dictionary[asin]["Future Maliyet"])
        for col_name in price_columns_list:
            future_name = col_name.lower().replace("price", "future price")
            write_dict[future_name].append(restock_dictionary[asin][future_name])

    if progress_callback:
        progress_callback("Hesaplanan veriler ana tabloya entegre ediliyor...")

    try:
        maliyet_index = restock_df.columns.get_loc("Maliyet") + 1
    except KeyError:
        maliyet_index = len(restock_df.columns)

    restock_df.insert(
        maliyet_index, "Future Price", future_price_list, allow_duplicates=False
    )
    restock_df.insert(
        maliyet_index + 1, "Future Maliyet", future_maliyet_list, allow_duplicates=False
    )

    dont_exist_list = []
    for future_name, vals in write_dict.items():
        name = future_name.replace("future price", "price")
        try:
            col_idx = restock_df.columns.get_loc(name) + 1
            restock_df.insert(col_idx, future_name, vals, allow_duplicates=False)
        except KeyError:
            dont_exist_list.append(future_name)

    if dont_exist_list:
        price_indices = [
            restock_df.columns.get_loc(col)
            for col in restock_df.columns
            if "price" in col.lower()
        ]
        max_index = max(price_indices) if price_indices else len(restock_df.columns) - 1
        for name in dont_exist_list:
            max_index += 1
            restock_df.insert(max_index, name, write_dict[name], allow_duplicates=False)

    if progress_callback:
        progress_callback("Sonuç dosyası kaydediliyor...")
    os.makedirs(path, exist_ok=True)

    if name.strip() == "":
        name = "Future_Price_Sonuc"

    output_file_path = os.path.join(path, f"{name}.xlsx")
    restock_df.to_excel(output_file_path, index=False)

    return {
        "status": "success",
        "message": "Future Price işlemi başarıyla tamamlandı!",
        "output_path": path,
    }
