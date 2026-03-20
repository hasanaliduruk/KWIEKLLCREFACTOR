import os
import shutil
import pandas as pd


def process_invoice_finder(
    source_excel: str,
    all_invoices_excel: str,
    invoice_pdf_folder: str,
    output_folder: str,
    user_input_date: str,
    progress_callback=None,
) -> dict:
    if not source_excel or not os.path.exists(source_excel):
        raise FileNotFoundError(
            "Hata: Kaynak Excel dosyası (Invoice Finder) bulunamadı."
        )
    if not all_invoices_excel or not os.path.exists(all_invoices_excel):
        raise FileNotFoundError("Hata: All Invoices Excel dosyası bulunamadı.")
    if not os.path.exists(invoice_pdf_folder):
        raise FileNotFoundError("Hata: Invoice PDF klasörü bulunamadı.")

    if progress_callback:
        progress_callback("Sağlanan kaynak excel dosyası okunuyor...")
    df = pd.read_excel(source_excel, header=None)
    lines = [str(line[0]) for line in df.values.tolist()]

    dictionary = {}
    if progress_callback:
        progress_callback("Dosyadan SKU ve Quantity değerleri ayrıştırılıyor...")

    for i, line in enumerate(lines):
        if line.count("_") >= 3:
            number_list = []
            for item in lines[i:]:
                if "FNSKU" in str(item):
                    idx = lines.index(item)
                    number_list = [
                        lines[idx],
                        lines[idx + 1] if idx + 1 < len(lines) else "0",
                    ]
                    break
            dictionary[line] = number_list

    upc_list = {}
    return_dictionary = {}
    excel_write_dictionary = {}
    atlanan_asinler = []

    for asin, number_list in dictionary.items():
        if not number_list:
            continue
        number = "#YOK"
        if "-" in str(number_list[1]):
            number = str(number_list[0])
        elif "+" in str(number_list[1]):
            number = str(number_list[1]).split("+")[0]

        split_asin = asin.split("_")
        if len(split_asin) < 3:
            continue
        upc, pk = split_asin[1], split_asin[2]
        pka = int(pk.replace("PK", "")) if "PK" in pk else 1

        deger = int(float(number)) * pka if number != "#YOK" else 0

        excel_write_dictionary[asin] = {
            "upc": upc,
            "pk": pk,
            "amazonshipquantity": deger,
            "invoice quantity": "",
            "item number": "",
            "invoice number": "",
            "invoice each": "",
            "invoice date": "",
            "Yapildi/Yapilmadi": "",
            "Fark": "",
        }

        if upc not in upc_list:
            upc_list[upc] = asin
            return_dictionary[asin] = {
                "upc": float(upc),
                "pk": pk,
                "amazonshipquantity": deger,
            }
        else:
            atlanan_asinler.append(asin)
            main_asin = upc_list[upc]
            return_dictionary[main_asin]["amazonshipquantity"] += deger

    if progress_callback:
        progress_callback("ALL INVOICES excel dosyası okunuyor...")
    df_all = pd.read_excel(all_invoices_excel)
    upcs, shipquantity = df_all["Upc"].tolist(), df_all["ShipQuantity"].tolist()
    shipitem, invoice_number = (
        df_all["ShipItem"].tolist(),
        df_all["InvoiceNumber"].tolist(),
    )
    date = df_all["Date"].tolist()

    user_date = pd.to_datetime(user_input_date, format="%d.%m.%Y", errors="coerce")
    if pd.isna(user_date):
        raise ValueError("Hatalı tarih formatı. Lütfen GG.AA.YYYY formatında giriniz.")

    invoices = os.listdir(invoice_pdf_folder)

    if progress_callback:
        progress_callback("Fatura eşleştirmesi ve PDF kopyalaması yapılıyor...")
    for SKU, data in return_dictionary.items():
        upc = data["upc"]
        indices = [i for i, x in enumerate(upcs) if x == upc]
        temporary_dict = {}

        if indices:
            for idx in indices:
                if pd.to_datetime(date[idx]) <= user_date:
                    temporary_dict[idx] = {
                        "shipquantity": shipquantity[idx],
                        "shipitem": shipitem[idx],
                        "invoice_number": invoice_number[idx],
                        "date": pd.to_datetime(date[idx]),
                    }

            a = 0
            dict_a = {"invoice": [], "itemid": [], "date": [], "b": []}

            # Tehlikeli recursive fonksiyon güvenli while döngüsüne çevrildi
            while temporary_dict and a < data["amazonshipquantity"]:
                max_date_key = max(
                    temporary_dict, key=lambda x: temporary_dict[x]["date"]
                )
                inv_num_str = str(temporary_dict[max_date_key]["invoice_number"])

                for file in invoices:
                    if inv_num_str in file:
                        shutil.copy2(
                            os.path.join(invoice_pdf_folder, file),
                            os.path.join(output_folder, file),
                        )
                        if inv_num_str not in dict_a["invoice"]:
                            dict_a["invoice"].append(inv_num_str)

                b = int(temporary_dict[max_date_key]["shipquantity"])
                a += b
                dict_a["itemid"].append(temporary_dict[max_date_key]["shipitem"])
                dict_a["date"].append(
                    temporary_dict[max_date_key]["date"].strftime("%d-%m-%Y")
                )
                dict_a["b"].append(b)
                temporary_dict.pop(max_date_key)

            excel_write_dictionary[SKU]["invoice quantity"] = a
            excel_write_dictionary[SKU]["invoice number"] = ", ".join(dict_a["invoice"])
            excel_write_dictionary[SKU]["item number"] = ", ".join(
                [str(int(x)) for x in dict_a["itemid"]]
            )
            excel_write_dictionary[SKU]["invoice date"] = ", ".join(dict_a["date"])
            excel_write_dictionary[SKU]["Yapildi/Yapilmadi"] = "Yapildi"
            excel_write_dictionary[SKU]["invoice each"] = ", ".join(
                [str(x) for x in dict_a["b"]]
            )
            fark = a - data["amazonshipquantity"]
            excel_write_dictionary[SKU]["Fark"] = f"+{fark}" if fark > 0 else fark
        else:
            excel_write_dictionary[SKU]["Yapildi/Yapilmadi"] = "Yapilmadi"

        if not excel_write_dictionary[SKU]["invoice number"]:
            excel_write_dictionary[SKU]["Yapildi/Yapilmadi"] = "Yapilmadi"

    for asin in atlanan_asinler:
        gercek_asin = upc_list[excel_write_dictionary[asin]["upc"]]
        for field in [
            "invoice each",
            "item number",
            "invoice number",
            "invoice quantity",
            "invoice date",
            "Yapildi/Yapilmadi",
            "Fark",
        ]:
            excel_write_dictionary[asin][field] = excel_write_dictionary[gercek_asin][
                field
            ]

    if progress_callback:
        progress_callback("Sonuç excel dosyası kaydediliyor...")
    df_out = pd.DataFrame.from_dict(
        excel_write_dictionary, orient="index"
    ).reset_index()
    df_out = df_out.rename(columns={"index": "SKU"})
    df_out.to_excel(os.path.join(output_folder, "sonexcel.xlsx"), index=False)

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
    if not all_invoices_excel or not os.path.exists(all_invoices_excel):
        raise FileNotFoundError("Hata: All Invoices Excel dosyası bulunamadı.")
    if not os.path.exists(invoice_pdf_folder):
        raise FileNotFoundError("Hata: Invoice PDF klasörü bulunamadı.")

    if progress_callback:
        progress_callback("ALL INVOICES excel dosyası okunuyor...")
    df = pd.read_excel(all_invoices_excel)
    upc_col = df["Upc"].tolist()
    invoice_number_col = df["InvoiceNumber"].tolist()
    date_col = pd.to_datetime(df["Date"])

    now_date = pd.Timestamp.now()
    try:
        int_month = int(months_str)
    except ValueError:
        raise ValueError("Geçersiz ay değeri. Lütfen tam sayı giriniz.")

    if int_month != 0:
        before_months = now_date - pd.DateOffset(months=int_month)
        if progress_callback:
            progress_callback(
                f"{int_month} ay öncesine kadar olan faturalar aranıyor..."
            )

    split_upc = [u.strip() for u in upcs_str.split(",") if u.strip()]
    if not split_upc:
        raise ValueError("Geçerli bir UPC değeri girilmedi.")

    found_any = False
    for upc in split_upc:
        try:
            f_upc = float(upc)
        except ValueError:
            continue

        indices = [i for i, x in enumerate(upc_col) if x == f_upc]
        for idx in indices:
            if int_month != 0 and date_col[idx] <= before_months:
                continue

            inv_num = str(invoice_number_col[idx])
            for file in os.listdir(invoice_pdf_folder):
                if inv_num in file:
                    found_any = True
                    target_dir = (
                        os.path.join(output_folder, str(upc))
                        if len(split_upc) > 1
                        else output_folder
                    )
                    os.makedirs(target_dir, exist_ok=True)
                    shutil.copy2(
                        os.path.join(invoice_pdf_folder, file),
                        os.path.join(target_dir, file),
                    )

    if not found_any:
        raise ValueError("Belirtilen kriterlere uygun hiçbir fatura PDF'i bulunamadı.")

    return {
        "status": "success",
        "message": "Faturalar başarıyla bulundu ve kopyalandı!",
        "output_path": output_folder,
    }
