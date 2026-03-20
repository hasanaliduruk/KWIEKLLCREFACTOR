import os
import math
import pandas as pd

def parse_shipment_settings(settings_content: str):
    sutunlar_dict = {
        'restock_upc': [], 'restock_pcs': [], 'restock_asin': [], 'restock_pk': [], 'restock_price': [], 'restock_suplier': [],
        'orderform_upc': [], 'orderform_pcs': [], 'orderform_asin': [], 'orderform_sku': [], 'orderform_pk': [], 'orderform_price': [], 'orderform_suplier': [],
        'invoice_shipquantity': [], 'invoice_upc': [], 'invoice_price': [], 'invoice_packsize':[], 'invoice_brand':[], 'invoice_description':[]
    }
    lines = [line.strip() for line in settings_content.split('\n') if line.strip()]
    section = 0
    for line in lines:
        if '=====' in line:
            section += 1
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip().lower()
            vals = [v.strip() for v in val.split(',')]
            
            if section == 0:
                if key == 'upc': sutunlar_dict['restock_upc'] = vals
                elif key == 'pcs': sutunlar_dict['restock_pcs'] = vals
                elif key == 'asin': sutunlar_dict['restock_asin'] = vals
                elif key == 'pk': sutunlar_dict['restock_pk'] = vals
                elif key == 'price': sutunlar_dict['restock_price'] = vals
                elif key == 'suplier': sutunlar_dict['restock_suplier'] = vals
            elif section == 1:
                if key == 'upc': sutunlar_dict['orderform_upc'] = vals
                elif key == 'pcs': sutunlar_dict['orderform_pcs'] = vals
                elif key == 'asin': sutunlar_dict['orderform_asin'] = vals
                elif key == 'sku': sutunlar_dict['orderform_sku'] = vals
                elif key == 'pk': sutunlar_dict['orderform_pk'] = vals
                elif key == 'price': sutunlar_dict['orderform_price'] = vals
                elif key == 'suplier': sutunlar_dict['orderform_suplier'] = vals
            elif section == 2:
                if key == 'shipquantity': sutunlar_dict['invoice_shipquantity'] = vals
                elif key == 'upc': sutunlar_dict['invoice_upc'] = vals
                elif key == 'price': sutunlar_dict['invoice_price'] = vals
                elif key == 'packsize': sutunlar_dict['invoice_packsize'] = vals
                elif key == 'brand': sutunlar_dict['invoice_brand'] = vals
                elif key == 'description': sutunlar_dict['invoice_description'] = vals
    return sutunlar_dict

def get_col(df, possible_cols, context):
    for col in possible_cols:
        if col in df.columns: return col
    raise ValueError(f"Eksik Sütun: {context} için beklenen sütunlardan hiçbiri bulunamadı. Beklenenler: {possible_cols}")

def indexFinder(item, liste):
    return [a for a, z in enumerate(liste) if z == item]

def process_shipment_creation(invoice_files: list, order_form_files: list, restock_files: list, output_folder: str, save_name: str, dc_code: str, settings_content: str, progress_callback=None) -> dict:
    if not invoice_files or not order_form_files or not restock_files:
        raise ValueError("Hata: Gerekli kaynak dosyalardan biri (Invoice, Order Form veya Restock) eksik.")
        
    sutunlar_dict = parse_shipment_settings(settings_content)
    
    # 1. INVOICE OKUMA
    if progress_callback: progress_callback("Invoice dosyası okunuyor...")
    df_inv = pd.read_excel(invoice_files[0])
    invoice_form_dict = {
        'ShipQuantity': df_inv[get_col(df_inv, sutunlar_dict['invoice_shipquantity'], 'Invoice ShipQuantity')].tolist(),
        'Upc': df_inv[get_col(df_inv, sutunlar_dict['invoice_upc'], 'Invoice UPC')].tolist(),
        'Price': df_inv[get_col(df_inv, sutunlar_dict['invoice_price'], 'Invoice Price')].tolist(),
        'PackSize': df_inv[get_col(df_inv, sutunlar_dict['invoice_packsize'], 'Invoice PackSize')].tolist(),
        'Brand': df_inv[get_col(df_inv, sutunlar_dict['invoice_brand'], 'Invoice Brand')].tolist(),
        'Description': df_inv[get_col(df_inv, sutunlar_dict['invoice_description'], 'Invoice Description')].tolist()
    }

    # 2. ORDER FORM OKUMA
    if progress_callback: progress_callback("Order Form dosyası okunuyor...")
    df_ord = pd.read_excel(order_form_files[0])
    order_form_dict = {
        'Upc': df_ord[get_col(df_ord, sutunlar_dict['orderform_upc'], 'OrderForm UPC')].tolist(),
        'Price': df_ord[get_col(df_ord, sutunlar_dict['orderform_price'], 'OrderForm Price')].tolist(),
        'Suplier': df_ord[get_col(df_ord, sutunlar_dict['orderform_suplier'], 'OrderForm Suplier')].tolist()
    }
    for i in range(1, len(sutunlar_dict['orderform_asin'])+1):
        col_name = sutunlar_dict['orderform_pcs'][0] if i == 1 else f"{sutunlar_dict['orderform_pcs'][0]}.{i-1}"
        order_form_dict[f'Pcs {i}'] = df_ord[get_col(df_ord, [col_name], f'OrderForm PCS {i}')].tolist()
    for a, name in enumerate(sutunlar_dict['orderform_asin'], 1):
        order_form_dict[f'Asin {a}'] = df_ord[get_col(df_ord, [name], f'OrderForm ASIN {a}')].tolist()
    for a, name in enumerate(sutunlar_dict['orderform_sku'], 1):
        order_form_dict[f'ASIN{a}_SKU'] = df_ord[get_col(df_ord, [name], f'OrderForm SKU {a}')].tolist()
        liste = [str(i).split('_')[2] if isinstance(i, str) and str(i).count('_') >= 3 else '#YOK' for i in order_form_dict[f'ASIN{a}_SKU']]
        order_form_dict[f'PK {a}'] = liste

    # 3. RESTOCK OKUMA
    if progress_callback: progress_callback("Restock dosyası okunuyor...")
    df_res = pd.read_excel(restock_files[0])
    restock_form_dict = {
        'Asin': df_res[get_col(df_res, sutunlar_dict['restock_asin'], 'Restock ASIN')].tolist(),
        'Upc': df_res[get_col(df_res, sutunlar_dict['restock_upc'], 'Restock UPC')].tolist(),
        'Pcs': df_res[get_col(df_res, sutunlar_dict['restock_pcs'], 'Restock PCS')].tolist(),
        'PK': df_res[get_col(df_res, sutunlar_dict['restock_pk'], 'Restock PK')].tolist(),
        'Price': df_res[get_col(df_res, sutunlar_dict['restock_price'], 'Restock Price')].tolist(),
        'Suplier': df_res[get_col(df_res, sutunlar_dict['restock_suplier'], 'Restock Suplier')].tolist()
    }

    # 4. EŞLEŞTİRME (MATCH)
    if progress_callback: progress_callback("UPC değerleri eşleniyor...")
    dictionary = {k: [] for k in ['UPC', 'Price', 'Price Check', 'Suplier', 'ShipQuantity', 'Asin', 'Pcs', 'Yeni Pcs', 'PK', 'SKU', 'PackSize', 'Brand', 'Description', 'DOSYA', 'SKU2', 'PK EACH', 'Kalan']}
    
    for upc in invoice_form_dict['Upc']:
        restock_kontrol = 1 if upc in restock_form_dict['Upc'] else 0
        order_kontrol = 1 if upc in order_form_dict['Upc'] else 0
        
        index_invoice = invoice_form_dict['Upc'].index(upc)
        Price = invoice_form_dict['Price'][index_invoice]
        ShipQuantity = invoice_form_dict['ShipQuantity'][index_invoice]
        PackSize = invoice_form_dict['PackSize'][index_invoice]
        Brand = invoice_form_dict['Brand'][index_invoice]
        Description = invoice_form_dict['Description'][index_invoice]
        upcstr = str(upc).zfill(12)

        if restock_kontrol:
            indices = indexFinder(upc, restock_form_dict['Upc'])
            for index in indices:
                Pcs = restock_form_dict['Pcs'][index]
                Pk = restock_form_dict['PK'][index]
                Pkint = int(str(Pk).replace('PK', '')) if Pk != '#YOK' else '#YOK'
                
                if not (isinstance(Pcs, float) and math.isnan(Pcs)):
                    dictionary['UPC'].append(upc)
                    dictionary['Price'].append(Price)
                    dictionary['Price Check'].append(restock_form_dict['Price'][index])
                    dictionary['Suplier'].append(restock_form_dict['Suplier'][index])
                    dictionary['ShipQuantity'].append(ShipQuantity)
                    dictionary['PackSize'].append(PackSize)
                    dictionary['Brand'].append(Brand)
                    dictionary['Description'].append(Description)
                    dictionary['Asin'].append(restock_form_dict['Asin'][index])
                    dictionary['Pcs'].append(Pcs)
                    dictionary['Yeni Pcs'].append(0)
                    dictionary['PK'].append(Pk)
                    dictionary['SKU'].append('#YOK')
                    dictionary['SKU2'].append(f"{dc_code}_{upcstr}_{Pk}_{format(Pkint * Price, '.2f')}" if Pkint != '#YOK' else '#YOK')
                    dictionary['PK EACH'].append(0)
                    dictionary['Kalan'].append(0)
                    dictionary['DOSYA'].append('Restock')

        if order_kontrol:
            indices = indexFinder(upc, order_form_dict['Upc'])
            for index in indices:
                a = 1
                while True:
                    try:
                        Asin = order_form_dict[f'Asin {a}'][index]
                        Pcs = order_form_dict[f'Pcs {a}'][index]
                        PK = order_form_dict[f'PK {a}'][index]
                        Pkint = int(str(PK).replace('PK', '')) if PK != '#YOK' else '#YOK'
                        
                        if pd.notna(Asin):
                            dictionary['UPC'].append(upc)
                            dictionary['Price'].append(Price)
                            dictionary['Price Check'].append(order_form_dict['Price'][index])
                            dictionary['Suplier'].append(order_form_dict['Suplier'][index])
                            dictionary['ShipQuantity'].append(ShipQuantity)
                            dictionary['PackSize'].append(PackSize)
                            dictionary['Brand'].append(Brand)
                            dictionary['Description'].append(Description)
                            dictionary['Asin'].append(Asin)
                            dictionary['Pcs'].append(Pcs)
                            dictionary['Yeni Pcs'].append(0)
                            dictionary['PK'].append(PK)
                            dictionary['SKU'].append(order_form_dict[f'ASIN{a}_SKU'][index])
                            dictionary['SKU2'].append(f"{dc_code}_{upcstr}_{PK}_{format(Pkint * Price, '.2f')}" if Pkint != '#YOK' else '#YOK')
                            dictionary['PK EACH'].append(0)
                            dictionary['Kalan'].append(0)
                            dictionary['DOSYA'].append('Order Form')
                        a += 1
                    except KeyError:
                        break
                        
        if not restock_kontrol and not order_kontrol:
            for k in dictionary.keys(): dictionary[k].append('#YOK')
            dictionary['UPC'][-1] = upc
            dictionary['Price'][-1] = Price
            dictionary['ShipQuantity'][-1] = ShipQuantity
            dictionary['PackSize'][-1] = PackSize
            dictionary['Brand'][-1] = Brand
            dictionary['Description'][-1] = Description
            dictionary['Yeni Pcs'][-1] = 0

    # Benzersiz SKU2 harflendirme
    letter_dictionary = {0: "", 1: "_A", 2: "_B", 3: "_C", 4: "_D", 5: "_E"}
    index_list = []
    for sku in dictionary['SKU2']:
        if sku == '#YOK': continue
        indexes = indexFinder(sku, dictionary['SKU2'])
        for i, idx in enumerate(indexes):
            if idx not in index_list and dictionary['SKU2'][idx] != '#YOK':
                dictionary['SKU2'][idx] += letter_dictionary.get(i, f"_{i}")
                index_list.append(idx)

    # 5. STOCK ALLOCATER
    if progress_callback: progress_callback("Stoklar dağıtılıyor...")
    complated_upc = []
    for upc in dictionary['UPC']:
        if upc not in complated_upc:
            complated_upc.append(upc)
            index_list = indexFinder(upc, dictionary['UPC'])
            pcs, ShipQuantity, oldpk = 0, 0, 9999999
            smallest = []
            
            for index in index_list:
                ShipQuantity = dictionary['ShipQuantity'][index]
                if dictionary['Pcs'][index] != '#YOK' and not pd.isna(dictionary['Pcs'][index]):
                    pcs += float(dictionary['Pcs'][index])
                if dictionary['PK'][index] != '#YOK':
                    nowpk = int(str(dictionary['PK'][index]).replace('PK', ''))
                    if nowpk <= oldpk:
                        oldpk = nowpk
                        smallest = [nowpk, index]
                        
            for index in index_list:
                if dictionary['Pcs'][index] != '#YOK' and not pd.isna(dictionary['Pcs'][index]) and pcs > 0:
                    new_pcs = round(float(dictionary['Pcs'][index]) / pcs * float(ShipQuantity))
                    pk = dictionary['PK'][index]
                    if pk != '#YOK':
                        pk = int(str(pk).replace('PK', ''))
                        kalan = new_pcs % pk
                        if index != smallest[1]:
                            dictionary['Yeni Pcs'][index] = new_pcs - kalan
                            dictionary['Yeni Pcs'][smallest[1]] += kalan
                        else:
                            dictionary['Yeni Pcs'][smallest[1]] += new_pcs
                    else:
                        dictionary['Yeni Pcs'][index] = new_pcs

            for index in index_list:
                pk = dictionary['PK'][index]
                if pk != '#YOK':
                    pk = int(str(pk).replace('PK', ''))
                    yenipcs = dictionary['Yeni Pcs'][index]
                    dictionary['PK EACH'][index] = int(yenipcs / pk)
                    dictionary['Kalan'][index] = yenipcs % pk

    if progress_callback: progress_callback("Sonuç Excel dosyasına kaydediliyor...")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f'{save_name}.xlsx')
    pd.DataFrame(dictionary).to_excel(output_path, index=False)
    
    return {"status": "success", "message": "Shipment Create işlemi başarıyla tamamlandı!", "output_path": output_folder}