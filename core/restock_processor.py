import os
import pandas as pd
import numpy as np


def find_column(df, possible_columns, error_msg):
    for column in possible_columns:
        if column in df.columns:
            return column
    raise ValueError(f"Eksik Sütun Hatası: {error_msg}")


def read_settings():
    sutun_dictionary = {
        "upc_sutunlari_olabilir": [],
        "brand_sutunlari_olabilir": [],
        "price_sutunlari_olabilir": [],
        "case_sutunlari_olabilir": [],
        "quantity_sutunlari_olabilir": [],
        "pk_sutunlari_olabilir": [],
    }
    maliyet_dict = {}

    with open("Settings/restock_settings.txt", "r", encoding="utf-8") as file:
        satirlar = file.readlines()

    a = 0
    for satir in satirlar:
        if "=====" in satir:
            a += 1
            continue

        if a == 0 and "=" in satir:
            key, val = satir.split("=", 1)
            key = key.strip().lower()
            vals = [v.strip() for v in val.split(",")]

            if key == "upc":
                sutun_dictionary["upc_sutunlari_olabilir"] = vals
            elif key == "brand":
                sutun_dictionary["brand_sutunlari_olabilir"] = vals
            elif key == "price":
                sutun_dictionary["price_sutunlari_olabilir"] = vals
            elif key == "case":
                sutun_dictionary["case_sutunlari_olabilir"] = vals
            elif key == "quantity on hand":
                sutun_dictionary["quantity_sutunlari_olabilir"] = vals
            elif key == "pk":
                sutun_dictionary["pk_sutunlari_olabilir"] = vals

        elif a == 1 and ":" in satir:
            key, val = satir.split(":", 1)
            maliyet_dict[key.strip()] = float(val.strip())

    return sutun_dictionary, maliyet_dict


def process_export(path, row_file, export_files, columns_dict, dataframe_dictionary):
    row_code = os.path.basename(row_file).split("-")[0]
    row_df = dataframe_dictionary[row_file]

    colrow = find_column(
        row_df,
        columns_dict["upc_sutunlari_olabilir"],
        f"{row_file} ham dosyası için UPC sütunu bulunamadı.",
    )
    row_upcs = set(row_df[colrow].tolist())

    export_file = next(
        (f for f in export_files if os.path.basename(f).split("-")[0] == row_code), None
    )
    if not export_file:
        raise ValueError(f"Eşleşen export dosyası bulunamadı: {row_code}")

    export_df = pd.read_excel(export_file, engine="openpyxl")
    colexp = find_column(
        export_df,
        columns_dict["upc_sutunlari_olabilir"],
        f"{export_file} export dosyası için UPC sütunu bulunamadı.",
    )
    qtycol = find_column(
        export_df,
        columns_dict["quantity_sutunlari_olabilir"],
        f"{export_file} export dosyası için Quantity sütunu bulunamadı.",
    )

    upcs = export_df[colexp].tolist()
    qtyonhand = export_df[qtycol].tolist()

    upcs_unique, idx = np.unique(upcs, return_index=True)
    qtyonhand_unique = [qtyonhand[i] for i in idx]
    qty_dict = pd.Series(qtyonhand_unique, index=upcs_unique)

    upcs_set = set(upcs)
    silinecek_degerler = row_upcs - upcs_set
    row_df = row_df[~row_df[colrow].isin(silinecek_degerler)].copy()

    price_sutun = find_column(
        row_df,
        columns_dict["price_sutunlari_olabilir"],
        f"{row_file} ham dosyası için Price sütunu bulunamadı.",
    )
    quantity_list = row_df[colrow].map(qty_dict).fillna("#YOK")

    try:
        price_index = row_df.columns.get_loc(price_sutun)
        row_df.insert(price_index + 1, "Qty on Hand", quantity_list, True)
    except KeyError:
        insert_idx = min(21, row_df.shape[1])
        row_df.insert(insert_idx, "Qty on Hand", quantity_list, True)

    save_path = os.path.join(path, "sonuclar", os.path.basename(row_file))
    row_df.to_excel(
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
    progress_callback=None,
):
    if not row_files:
        raise ValueError("Ham dosyalar (Row files) eksik.")

    os.makedirs(os.path.join(path, "sonuclar"), exist_ok=True)
    columns_dict, maliyet_dict = read_settings()
    dataframe_dictionary = {}

    # 1. DOSYALARI OKUMA
    for i, file in enumerate(row_files):
        if progress_callback:
            progress_callback(
                f"Okunuyor ({i+1}/{len(row_files)}): {os.path.basename(file)}", 10
            )
        dataframe_dictionary[file] = pd.read_excel(file, engine="openpyxl")

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

    # 3. BİRBİRİNDEN DÜŞME TESPTİ
    if progress_callback:
        progress_callback("Silinecek UPC değerleri tespit ediliyor...", 50)
    remove_upc = {file: [] for file in row_files}
    for i, file in enumerate(row_files):
        this_df = dataframe_dictionary[file]
        upc_col = find_column(
            this_df,
            columns_dict["upc_sutunlari_olabilir"],
            f"{file} için UPC bulunamadı.",
        )
        price_col = find_column(
            this_df,
            columns_dict["price_sutunlari_olabilir"],
            f"{file} için Price bulunamadı.",
        )
        this_upc_dict = this_df.set_index(upc_col)[price_col].to_dict()

        for next_file in row_files[i + 1 :]:
            next_df = dataframe_dictionary[next_file]
            n_upc_col = find_column(
                next_df,
                columns_dict["upc_sutunlari_olabilir"],
                f"{next_file} için UPC bulunamadı.",
            )
            n_price_col = find_column(
                next_df,
                columns_dict["price_sutunlari_olabilir"],
                f"{next_file} için Price bulunamadı.",
            )
            next_upc_dict = next_df.set_index(n_upc_col)[n_price_col].to_dict()

            for upc, price in this_upc_dict.items():
                if upc in next_upc_dict:
                    if price < next_upc_dict[upc]:
                        remove_upc[next_file].append(upc)
                    elif price > next_upc_dict[upc]:
                        remove_upc[file].append(upc)
                    else:
                        remove_upc[next_file].append(upc)

    # 4. BİRBİRİNDEN DÜŞME UYGULAMA
    row_dataframe_dictionary = {}
    for i, file in enumerate(row_files):
        if progress_callback:
            progress_callback(f"UPC'ler siliniyor: {os.path.basename(file)}", 60)
        df = dataframe_dictionary[file]
        upc_col = find_column(
            df, columns_dict["upc_sutunlari_olabilir"], f"{file} için UPC bulunamadı."
        )
        df_filtered = df[~df[upc_col].isin(remove_upc[file])]

        save_path = os.path.join(path, "sonuclar", os.path.basename(file))
        mode = "a" if islem.get("export") == 1 and os.path.exists(save_path) else "w"

        if mode == "a":
            with pd.ExcelWriter(save_path, engine="openpyxl", mode="a") as writer:
                df_filtered.to_excel(writer, sheet_name="dusulmus liste", index=False)
        else:
            df_filtered.to_excel(save_path, sheet_name="dusulmus liste", index=False)

        row_dataframe_dictionary[file] = df_filtered

    # 5. RESTOCK
    if islem.get("restock") == 1:
        if not restock_files:
            raise ValueError("Restock (Ana) excel dosyası eksik.")
        if progress_callback:
            progress_callback("Restock birleştirmesi yapılıyor...", 70)

        main_excel = restock_files[0]
        yazilacak_dictionary = {}
        main_excel_df = pd.read_excel(main_excel, engine="openpyxl")
        lenght = main_excel_df.shape[1]

        main_upc_col = find_column(
            main_excel_df,
            columns_dict["upc_sutunlari_olabilir"],
            f"{main_excel} için UPC bulunamadı.",
        )
        main_upc_list = main_excel_df[main_upc_col].tolist()
        main_pk_col = find_column(
            main_excel_df,
            columns_dict["pk_sutunlari_olabilir"],
            f"{main_excel} için PK bulunamadı.",
        )
        main_pk_list = main_excel_df[main_pk_col].tolist()

        main_dict = {}
        for i, upc in enumerate(main_upc_list):
            main_dict[i] = {
                "upc": upc,
                "brand": "#YOK",
                "suplier": "#YOK",
                "price": "#YOK",
                "case": "#YOK",
                "qtyonhand": "#YOK",
                "PK": main_pk_list[i],
                "maliyet": "#YOK",
            }

        for i, file in enumerate(row_files):
            row_upc_col = find_column(
                row_dataframe_dictionary[file],
                columns_dict["upc_sutunlari_olabilir"],
                "UPC Yok",
            )
            row_case_col = find_column(
                row_dataframe_dictionary[file],
                columns_dict["case_sutunlari_olabilir"],
                "Case Yok",
            )
            row_quantity_col = find_column(
                row_dataframe_dictionary[file],
                columns_dict["quantity_sutunlari_olabilir"],
                "Quantity Yok",
            )

            export_upc_col = find_column(
                dataframe_dictionary[file],
                columns_dict["upc_sutunlari_olabilir"],
                "UPC Yok",
            )
            export_price_col = find_column(
                dataframe_dictionary[file],
                columns_dict["price_sutunlari_olabilir"],
                "Price Yok",
            )
            export_brand_col = find_column(
                dataframe_dictionary[file],
                columns_dict["brand_sutunlari_olabilir"],
                "Brand Yok",
            )
            export_quantity_col = find_column(
                dataframe_dictionary[file],
                columns_dict["quantity_sutunlari_olabilir"],
                "Quantity Yok",
            )

            row_upc_list = row_dataframe_dictionary[file][row_upc_col].tolist()
            row_case_list = row_dataframe_dictionary[file][row_case_col].tolist()
            row_quantity_list = row_dataframe_dictionary[file][
                row_quantity_col
            ].tolist()

            export_upc_list = dataframe_dictionary[file][export_upc_col].tolist()
            export_price_list = dataframe_dictionary[file][export_price_col].tolist()
            export_brand_list = dataframe_dictionary[file][export_brand_col].tolist()
            export_quantity_list = dataframe_dictionary[file][
                export_quantity_col
            ].tolist()

            export_dict = {}
            for j, upc in enumerate(export_upc_list):
                export_dict[upc] = {
                    "price": export_price_list[j],
                    "quantity": export_quantity_list[j],
                    "brand": export_brand_list[j],
                }

            row_dict = {}
            for j, upc in enumerate(row_upc_list):
                row_dict[upc] = {
                    "case": row_case_list[j],
                    "quantity": row_quantity_list[j],
                }

            yazilacak_dictionary[file] = {"price": [], "quantity": []}

            for index in main_dict.keys():
                upc = main_dict[index]["upc"]
                if upc in export_upc_list:
                    x = True
                    if main_dict[index].keys() != []:
                        for key in main_dict[index].keys():
                            if str(key).endswith(".xlsx"):
                                if main_dict[index][key]["price"] != "#YOK":
                                    if (
                                        main_dict[index][key]["price"]
                                        > export_dict[upc]["price"]
                                    ):
                                        pass
                                    elif (
                                        main_dict[index][key]["price"]
                                        < export_dict[upc]["price"]
                                    ):
                                        x = False
                                        break
                    main_dict[index][file] = {}
                    main_dict[index][file]["quantity"] = export_dict[upc]["quantity"]
                    main_dict[index][file]["price"] = export_dict[upc]["price"]
                    main_dict[index]["brand"] = export_dict[upc]["brand"]
                    if x == True:
                        main_dict[index]["price"] = export_dict[upc]["price"]
                else:
                    main_dict[index][file] = {"quantity": "#YOK", "price": "#YOK"}

                yazilacak_dictionary[file]["price"].append(
                    main_dict[index][file]["price"]
                )
                yazilacak_dictionary[file]["quantity"].append(
                    main_dict[index][file]["quantity"]
                )

                filename = os.path.basename(file).split("-")[0]
                if upc in row_upc_list:
                    main_dict[index]["suplier"] = filename
                    main_dict[index]["case"] = row_dict[upc]["case"]
                    main_dict[index]["qtyonhand"] = row_dict[upc]["quantity"]

        if progress_callback:
            progress_callback("Restock dosyası kaydediliyor...", 90)

        brand_list, suplier_list, price_list, case_list, quantity_list, maliyet_list = (
            [],
            [],
            [],
            [],
            [],
            [],
        )
        for index in main_dict.keys():
            brand_list.append(main_dict[index]["brand"])
            suplier_list.append(main_dict[index]["suplier"])
            price_list.append(main_dict[index]["price"])
            case_list.append(main_dict[index]["case"])
            quantity_list.append(main_dict[index]["qtyonhand"])

            if main_dict[index]["PK"] != "#YOK" and main_dict[index]["price"] != "#YOK":
                try:
                    pk = int(str(main_dict[index]["PK"]).replace("PK", ""))
                    maliyet_list.append(
                        (pk * float(main_dict[index]["price"]))
                        + float(maliyet_dict[main_dict[index]["suplier"]])
                    )
                except Exception:
                    maliyet_list.append(main_dict[index]["price"])
            else:
                maliyet_list.append(main_dict[index]["price"])

        main_excel_df.insert(lenght, "Brand", brand_list, True)
        main_excel_df.insert(lenght + 1, "Price", price_list, True)
        main_excel_df.insert(lenght + 2, "Maliyet", maliyet_list, True)
        main_excel_df.insert(lenght + 3, "Case", case_list, True)

        a = 4
        for file in yazilacak_dictionary.keys():
            filename = os.path.basename(file).split("-")[0]
            main_excel_df.insert(
                lenght + a,
                filename + " price",
                yazilacak_dictionary[file]["price"],
                True,
            )
            a += 1

        main_excel_df.insert(lenght + a, "Qty on Hand", quantity_list, True)
        a += 1

        for file in yazilacak_dictionary.keys():
            filename = os.path.basename(file).split("-")[0]
            main_excel_df.insert(
                lenght + len(yazilacak_dictionary.keys()) + a,
                filename + " quantity",
                yazilacak_dictionary[file]["quantity"],
                True,
            )
            a += 1

        main_excel_df.insert(
            lenght + len(yazilacak_dictionary.keys()) + a, "suplier", suplier_list, True
        )

        try:
            silme_kosul = ~main_excel_df["Price"].isin(["#YOK", "#YOK"])
            main_excel_df = main_excel_df[silme_kosul]
        except Exception:
            pass

        os.makedirs(os.path.join(path, "restock"), exist_ok=True)
        main_excel_df.to_excel(
            os.path.join(path, "restock", f"{save_name}.xlsx"),
            index=False,
            sheet_name="restock",
            engine="openpyxl",
        )

    if progress_callback:
        progress_callback("Tüm işlemler başarıyla tamamlandı!", 100)
    return {"status": "success", "output_path": path}
