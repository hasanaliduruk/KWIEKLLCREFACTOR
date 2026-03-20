"""
This project made by HASAN ALI DURUK
Duruk/'s Software LLC
"""

from utils.gui_helpers import open_folder_in_explorer, dark_title_bar, Error_box, text_print, hata_print, silici, width_f, smooth_scroll, color_change
from utils.file_operations import browse_directory, browse_excel, placeholder_finder, placeholder_saver, save_location_saver, path_text_function, relative_to_assets, write_settings
from utils.event_handlers import on_focus_in, on_focus_out, on_click_outside, on_mouse_wheel, on_text_enter, on_text_leave, on_button_click, button_hover, button_leave, show_menu
from gui.components.animated_image import AnimatedImage
from gui.components.choosers import ConvertChooser, PathAdressGroup
from gui.components.custom_buttons import MyButton, SwitchButton
from gui.components.option_menu import CustomOptionMenu
from gui.components.scrollbar import MyScrollbar
from gui.components.round_button import create_round_button
from gui.components.drag_drop import ham_drag_drop2, drag_drop
from gui.views.tsv_view import render_tsv_view
from gui.views.costupdater_view import render_costupdater_view
from gui.views.restock_view import render_restock_view
from gui.views.invoice_view import render_invoice_view
from gui.views.converter_view import render_converter_view
from gui.views.invoicefinder_view import render_invoicefinder_view
from gui.views.ordercreate_view import render_ordercreate_view
from gui.views.updater_view import render_updater_view
from gui.views.shipmentcreater_view import shipmentCreater
from core.invoice_processor import process_invoice
from core.converter import process_conversion
from core.shipment_creator import process_shipment_creation
from core.invoice_finder import process_invoice_finder, process_invoice_finder_upc
from core.future_price_updater import process_future_price

import socket
from threading import Thread
import tkinter
import tempfile
import subprocess
import signal

from screeninfo import get_monitors
from tkinter import messagebox
import os
import sys
import traceback
import pandas as pd
import numpy as np
import openpyxl
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import Pool, freeze_support


from pathlib import Path
from PIL import Image as HASAN
from PIL import ImageTk, ImageDraw

from tkinter import *


from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import tkinter as tk
import requests
from bs4 import BeautifulSoup



from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk
from xlsxwriter import Workbook
import csv
import math
import ctypes as ct
import shutil
from openpyxl import load_workbook

import lxml
import warnings
from bs4 import XMLParsedAsHTMLWarning
import platform

def find_column(df, possible_columns, Error):
    # DataFrame'de verilen olası UPC sütun adlarını arar ve ilk bulduğunu döner.
    # Eğer hiçbiri bulunamazsa, None döner.
    
    for column in possible_columns:
        if column in df.columns:
            return column

    messagebox.showerror('Error', 'Error: {}'.format(Error))
    return None

def file_reader(file):
    row_df = pd.read_excel(file, engine='openpyxl')
    return [file, row_df]

def export(liste): #liste must include (path, row, export_files, columns_dict, dataframe_dictionary)
    path = liste[0]
    row = liste[1]
    export_files = liste[2]
    columns_dict = liste[3]
    dataframe_dictionary = liste[4]

    row_code = row.split('/')[-1].split('-')[0]
    row_df = dataframe_dictionary[row]
    colrow = find_column(row_df, columns_dict['upc_sutunlari_olabilir'], f'{row} ham dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
    row_upcs = set(row_df[colrow].tolist())
    export_file = next((file for file in export_files if file.split('/')[-1].split('-')[0] == row_code), None)
    export_df = pd.read_excel(export_file, engine='openpyxl')
    colexp = find_column(export_df, columns_dict['upc_sutunlari_olabilir'], f'{row} export dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
    upcs = export_df[colexp].tolist()
    qtycol = find_column(export_df, columns_dict['quantity_sutunlari_olabilir'], f'{row} export dosyası için Quantity sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
    qtyonhand = export_df[qtycol].tolist()
    upcs_unique, idx = np.unique(upcs, return_index=True)
    qtyonhand_unique = [qtyonhand[i] for i in idx]

    qty_dict = pd.Series(qtyonhand_unique, index=upcs_unique)

    upcs_set = set(upcs)

    # silinecek değerleri belirlemek
    silinecek_degerler = row_upcs - upcs_set
    kosul = ~row_df[colrow].isin(silinecek_degerler)
    row_df = row_df[kosul]
    price_sutun = find_column(row_df, columns_dict['price_sutunlari_olabilir'], f'{row} ham dosyası için Price sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
    savename = row.split('/')[-1]
    uzunluk = row_df.shape[1]
    quantity_list = row_df[colrow].map(qty_dict).fillna('#YOK')
    try:
        price_index = row_df.columns.get_loc(price_sutun)
        row_df.insert(price_index+1, 'Qty on Hand', quantity_list, True)
    except:
        if uzunluk < 21:
            row_df.insert(uzunluk, 'Qty on Hand', quantity_list, True)
        elif uzunluk >= 21:
            row_df.insert(21, 'Qty on Hand', quantity_list, True)


    row_df.to_excel(r"{}/sonuclar/{}".format(path, savename), index=False, sheet_name='export sonuc', engine='xlsxwriter')
    return [row, row_df]

def birbirinden_dusme_remove(liste): #liste must include [file_name, remove_upc, dataframe_dictionary, path, columns_dictionary]
    file_name = liste[0]
    remove_upc = liste[1]
    dataframe_dictionary = liste[2]
    path = liste[3]
    columns_dictionary = liste[4]
    islem = liste[5]
    upc_column = find_column(dataframe_dictionary[file_name], columns_dictionary['upc_sutunlari_olabilir'], f'{file_name} dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
    kosul = ~dataframe_dictionary[file_name][upc_column].isin(remove_upc[file_name])
    dataframe_dictionary[file_name] = dataframe_dictionary[file_name][kosul]
    save_name = os.path.basename(file_name)
    save_path = os.path.join(path, 'sonuclar', save_name)
    save_path = str(save_path)
    if islem == 1:
        with pd.ExcelWriter(save_path, engine='openpyxl', mode='a') as writer:
            dataframe_dictionary[file_name].to_excel(writer, sheet_name='dusulmus liste', index=False)
    else:
        dataframe_dictionary[file_name].to_excel(save_path, sheet_name='dusulmus liste', index=False)
    return [file_name, dataframe_dictionary[file_name]]

def rest(path, row_files, export_files, restock_files, islem, progress_bar, output_text, save_name):
    def folder_creater(path):
        try:
            os.mkdir(f'{path}/sonuclar')
        except FileExistsError:
            pass

    def settings():
        with open('Settings/restock_settings.txt', 'w', encoding='utf-8') as file:
            file.write('41 cost\n'
                       '41 standart\n'
                       '45 standart\n'
                       '45 cost\n'
                       '19 cost\n'
                       '19 standart\n'
                       '27 cost\n'
                       '27 standart\n'
                       '18 cost\n'
                       '18 standart\n'
                       '01 cost\n'
                       '01 standart\n'
                       'NF\n'
                       '======================================\n'
                       "upc = UPC, upc, Upc, UPC #\n"
                       "brand = BRAND, Brand, brand\n"
                       "price = NET_AMOUNT, Price, price\n"
                       "case = CASEPACK, Size, Case, case, size\n"
                       "Quantity on hand = Qty on Hand, Quantity Available\n"
                       "pk = PK\n"
                       "======================================\n"
                       "41 cost: 0.78\n"
                       "41 standart: 0.78\n"
                       "45 cost: 0.78\n"
                       "45 standart: 0.78\n"
                       "19 cost: 0.78\n"
                       "19 standart: 0.78\n"
                       "27 cost: 1.10\n"
                       "27 standart: 1.10\n"
                       "18 cost: 1.10\n"
                       "18 standart: 1.10\n"
                       "01 cost: 1.10\n"
                       "01 standart: 1.10\n"
                       "NF: 0.78")

            file.close()

    def settings_reader():
        with open('Settings/restock_settings.txt', 'r', encoding='utf-8') as file:
            sutun_dictionary = {
                'upc_sutunlari_olabilir': [],
                'brand_sutunlari_olabilir': [],
                'price_sutunlari_olabilir': [],
                'case_sutunlari_olabilir': [],
                'quantity_sutunlari_olabilir': [],
                'pk_sutunlari_olabilir': []
            }

            satirlar = file.readlines()

            for satir in satirlar:
                ayrilmis = satir.split('=')
                if ayrilmis[0] == 'upc ' or ayrilmis[0] == 'upc':
                    for i in ayrilmis[1].split(','):
                        i = i.replace(' ', '',1)
                        i = i.replace('\n', '')
                        sutun_dictionary['upc_sutunlari_olabilir'].append(i)
                elif ayrilmis[0] == 'brand ' or ayrilmis[0] == 'brand':
                    for i in ayrilmis[1].split(','):
                        i = i.replace(' ', '',1)
                        i = i.replace('\n', '')
                        sutun_dictionary['brand_sutunlari_olabilir'].append(i)
                elif ayrilmis[0] == 'price ' or ayrilmis[0] == 'price':
                    for i in ayrilmis[1].split(','):
                        i = i.replace(' ', '',1)
                        i = i.replace('\n', '')
                        sutun_dictionary['price_sutunlari_olabilir'].append(i)
                elif ayrilmis[0] == 'case ' or ayrilmis[0] == 'case':
                    for i in ayrilmis[1].split(','):
                        i = i.replace(' ', '',1)
                        i = i.replace('\n', '')
                        sutun_dictionary['case_sutunlari_olabilir'].append(i)
                elif ayrilmis[0] == 'Quantity on hand ' or ayrilmis[0] == 'Quantity on hand':
                    for i in ayrilmis[1].split(','):
                        i = i.replace(' ', '', 1)
                        i = i.replace('\n', '')
                        sutun_dictionary['quantity_sutunlari_olabilir'].append(i)
                elif ayrilmis[0] == 'pk' or ayrilmis[0] == 'pk ':
                    for i in ayrilmis[1].split(','):
                        i = i.replace(' ', '', 1)
                        i = i.replace('\n', '')
                        sutun_dictionary['pk_sutunlari_olabilir'].append(i)
            a = 0
            maliyet_dict = {}
            for satir in satirlar:
                if '=====' in satir:
                    a += 1
                    continue
                if a == 1:
                    satir = satir.split(':')
                    satir[1] = satir[1].replace(' ', '')
                    maliyet_dict[satir[0]] = float(satir[1].replace('\n', ''))
        return [sutun_dictionary, maliyet_dict]

    #def export()

    def birbirinden_dusme(row_files, dataframe_dictionary, columns_dict):
        remove_upc = {file: [] for file in row_files}
        for i, file in enumerate(row_files):
            this_file_df = dataframe_dictionary[file]
            upc_column = find_column(this_file_df, columns_dict['upc_sutunlari_olabilir'], f'{file} dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            price_column = find_column(this_file_df, columns_dict['price_sutunlari_olabilir'], f'{file} dosyası için Price sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            this_file_upc = this_file_df.set_index(upc_column)[price_column].to_dict()
            a = i+1
            while a < len(row_files):
                next_file_name = row_files[a]
                next_file_df = dataframe_dictionary[next_file_name]
                upc_column = find_column(next_file_df, columns_dict['upc_sutunlari_olabilir'], f'{next_file_name} dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
                price_column = find_column(next_file_df, columns_dict['price_sutunlari_olabilir'], f'{next_file_name} dosyası için Price sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
                next_file_upc = next_file_df.set_index(upc_column)[price_column].to_dict()
                for upc in this_file_upc.keys():
                    if upc in next_file_upc.keys():
                        if this_file_upc[upc] < next_file_upc[upc]:
                            remove_upc[next_file_name].append(upc)
                        elif this_file_upc[upc] > next_file_upc[upc]:
                            remove_upc[file].append(upc)
                        elif this_file_upc[upc] == next_file_upc[upc]:
                            remove_upc[next_file_name].append(upc)
                a+=1
        return remove_upc

    #def birbirinden_dusme_remove()

    def restock(path, row_dataframe_dictionary, export_dataframe_dictionary, file_names, main_excel, columns_dict, maliyet_dict, save_name):
        yazilacak_dictionary = {}
        main_excel_df = pd.read_excel(main_excel, engine='openpyxl')
        lenght = main_excel_df.shape[1]
        main_upc_col = find_column(main_excel_df, columns_dict['upc_sutunlari_olabilir'], f'{main_excel} dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
        main_upc_list = main_excel_df[main_upc_col].tolist()
        main_pk_col = find_column(main_excel_df, columns_dict['pk_sutunlari_olabilir'], f'{main_excel} dosyası için PK sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
        main_pk_list = main_excel_df[main_pk_col].tolist()
        main_dict = {}
        for i, upc in enumerate(main_upc_list):
            main_dict[i] = {}
            main_dict[i]['upc'] = main_upc_list[i]
            main_dict[i]['brand'] = '#YOK'
            main_dict[i]['suplier'] = '#YOK'
            main_dict[i]['price'] = '#YOK'
            main_dict[i]['case'] = '#YOK'
            main_dict[i]['qtyonhand'] = '#YOK'
            main_dict[i]['PK'] = main_pk_list[i]
            main_dict[i]['maliyet'] = '#YOK'
        progress_bar['maximum'] = len(row_files)
        progress_bar['value'] = 0
        for i, file in enumerate(file_names):
            row_upc_col = find_column(row_dataframe_dictionary[file], columns_dict['upc_sutunlari_olabilir'], f'{file} ham dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            row_case_col = find_column(row_dataframe_dictionary[file], columns_dict['case_sutunlari_olabilir'], f'{file} ham dosyası için Case sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            row_quantity_col = find_column(row_dataframe_dictionary[file], columns_dict['quantity_sutunlari_olabilir'], f'{file} ham dosyası için Quantity sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            export_upc_col = find_column(export_dataframe_dictionary[file], columns_dict['upc_sutunlari_olabilir'], f'{file} export dosyası için UPC sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            export_price_col = find_column(export_dataframe_dictionary[file], columns_dict['price_sutunlari_olabilir'], f'{file} export dosyası için Price sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            export_brand_col = find_column(export_dataframe_dictionary[file], columns_dict['brand_sutunlari_olabilir'], f'{file} export dosyası için Brand sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')
            export_quantity_col = find_column(export_dataframe_dictionary[file], columns_dict['quantity_sutunlari_olabilir'], f'{file} export dosyası için Quantity sütunu bulunamadı, sütunların isimlerini kontrol edip tekrar deneyiniz!')

            row_upc_list = row_dataframe_dictionary[file][row_upc_col].tolist()
            row_case_list = row_dataframe_dictionary[file][row_case_col].tolist()
            row_quantity_list = row_dataframe_dictionary[file][row_quantity_col].tolist()
            export_upc_list = export_dataframe_dictionary[file][export_upc_col].tolist()
            export_price_list = export_dataframe_dictionary[file][export_price_col].tolist()
            export_brand_list = export_dataframe_dictionary[file][export_brand_col].tolist()
            export_quantity_list = export_dataframe_dictionary[file][export_quantity_col].tolist()

            export_dict = {}
            for i, upc in enumerate(export_upc_list):
                export_dict[upc] = {}
                export_dict[upc]['price'] = export_price_list[i]
                export_dict[upc]['quantity'] = export_quantity_list[i]
                export_dict[upc]['brand'] = export_brand_list[i]
            row_dict = {}
            for i, upc in enumerate(row_upc_list):
                row_dict[upc] = {}
                row_dict[upc]['case'] = row_case_list[i]
                row_dict[upc]['quantity'] = row_quantity_list[i]
            yazilacak_dictionary[file] = {
                'price': [],
                'quantity': []
            }
            for index in main_dict.keys():
                upc = main_dict[index]['upc']
                if upc in export_upc_list:
                    x = True
                    if main_dict[index].keys() != []:
                        for key in main_dict[index].keys():
                            if key.endswith('.xlsx'):
                                if main_dict[index][key]['price'] != '#YOK':
                                    if main_dict[index][key]['price'] > export_dict[upc]['price']:
                                        pass
                                    elif main_dict[index][key]['price'] < export_dict[upc]['price']:
                                        x = False
                                        break
                    main_dict[index][file] = {}
                    main_dict[index][file]['quantity'] = export_dict[upc]['quantity']
                    main_dict[index][file]['price'] = export_dict[upc]['price']
                    main_dict[index]['brand'] = export_dict[upc]['brand']
                    if x == True:
                        main_dict[index]['price'] = export_dict[upc]['price']
                else:
                    main_dict[index][file] = {}
                    main_dict[index][file]['quantity'] = '#YOK'
                    main_dict[index][file]['price'] = '#YOK'
                yazilacak_dictionary[file]['price'].append(main_dict[index][file]['price'])
                yazilacak_dictionary[file]['quantity'].append(main_dict[index][file]['quantity'])
                filesplit = file.split('/')[-1].split('-')
                filename = filesplit[0]
                if upc in row_upc_list:
                    main_dict[index]['suplier'] = filename
                    main_dict[index]['case'] = row_dict[upc]['case']
                    main_dict[index]['qtyonhand'] = row_dict[upc]['quantity']
            progress_bar['value'] = i+1
        text_print(output_text, 'Restock dosyası kaydediliyor...')
        progress_bar['maximum'] = 1
        progress_bar['value'] = 0
        brand_list = []
        suplier_list = []
        price_list = []
        case_list = []
        quantity_list = []
        maliyet_list = []
        for index in main_dict.keys():
            brand_list.append(main_dict[index]['brand'])
            suplier_list.append(main_dict[index]['suplier'])
            price_list.append(main_dict[index]['price'])
            case_list.append(main_dict[index]['case'])
            quantity_list.append(main_dict[index]['qtyonhand'])
            if main_dict[index]['PK'] != '#YOK' and main_dict[index]['price'] != '#YOK':
                try:
                    pk = int(main_dict[index]['PK'].replace('PK', ''))
                    maliyet_list.append((pk * float(main_dict[index]['price'])) + float(maliyet_dict[main_dict[index]['suplier']]))
                except:
                    maliyet_list.append(main_dict[index]['price'])
            else:
                maliyet_list.append(main_dict[index]['price'])


        main_excel_df.insert(lenght, 'Brand', brand_list, True)
        main_excel_df.insert(lenght+1, 'Price', price_list, True)
        main_excel_df.insert(lenght+2, 'Maliyet', maliyet_list, True)
        main_excel_df.insert(lenght+3, 'Case', case_list, True)
        a = 4
        for file in yazilacak_dictionary.keys():
            filesplit = file.split('/')[-1].split('-')
            filename = filesplit[0]
            main_excel_df.insert(lenght+a, filename + ' price', yazilacak_dictionary[file]['price'], True)
            a+=1
        main_excel_df.insert(lenght+a, 'Qty on Hand', quantity_list, True)
        a = 5
        for file in yazilacak_dictionary.keys():
            filesplit = file.split('/')[-1].split('-')
            filename = filesplit[0]

            main_excel_df.insert(lenght + len(yazilacak_dictionary.keys())+a, filename + ' quantity', yazilacak_dictionary[file]['quantity'], True)
            a+=1
        main_excel_df.insert(lenght + len(yazilacak_dictionary.keys())+a, 'suplier', suplier_list, True)
        try:
            silme_kosul = ~main_excel_df['Price'].isin(['#YOK', '#YOK'])
            main_excel_df = main_excel_df[silme_kosul]
        except:
            pass

        try:
            os.mkdir('{}/restock'.format(path))
        except FileExistsError:
            pass

        main_excel_df.to_excel('{}/restock/{}.xlsx'.format(path, save_name), index=False, sheet_name='restock', engine='xlsxwriter')
        progress_bar['value'] = 1
        return main_upc_list

    def main():
        folder_creater(path)

        dataframe_dictionary = {}
        if 'restock_settings.txt' not in os.listdir('Settings'):
            settings()
        sets = settings_reader()
        columns_dict = sets[0]
        maliyet_dict = sets[1]

        text_print(output_text, 'Ham dosyalar okunuyor...')

        ###    DOSYALARI OKUMA    ###
        progress_bar['maximum'] = len(row_files)
        progress_bar['value'] = 0
        p0 = Pool()
        for i, a in enumerate(p0.imap_unordered(file_reader, row_files)):
            dataframe_dictionary[a[0]] = a[1]
            progress_bar['value'] = i + 1
        p0.close()
        p0.join()
        ###################################################

        if islem['export'] == 1:
            text_print(output_text, 'Export işlemi yapılıyor...')
            ###    EXPORT POOL    ###
            export_multiprocess_list = []
            for row in row_files:
                tmp = [path, row, export_files, columns_dict, dataframe_dictionary]
                export_multiprocess_list.append(tmp)

            progress_bar['maximum'] = len(export_multiprocess_list)
            progress_bar['value'] = 0
            p1 = Pool()
            for i, a in enumerate(p1.imap_unordered(export, export_multiprocess_list)):
                dataframe_dictionary[a[0]] = a[1]
                progress_bar['value'] = i + 1
            p1.close()
            p1.join()
            ################################################

        #Silinecek UPC degerleri
        text_print(output_text, 'Silinecek UPC değerleri tespit ediliyor...')
        remove_upc = birbirinden_dusme(row_files, dataframe_dictionary, columns_dict)
        ################################################


        ###    BIRBIRINDEN DUSME POOL    ###
        text_print(output_text, 'Tespit edilen UPC değerleri siliniyor...')
        row_dataframe_dictionary = {}
        dusme_multiprocess_list = []
        for row in row_files:
            tmp = [row, remove_upc, dataframe_dictionary, path, columns_dict, islem['export']]
            dusme_multiprocess_list.append(tmp)

        progress_bar['maximum'] = len(dusme_multiprocess_list)
        progress_bar['value'] = 0
        p2 = Pool()
        for i, a in enumerate(p2.imap_unordered(birbirinden_dusme_remove, dusme_multiprocess_list)):
            row_dataframe_dictionary[a[0]] = a[1]
            progress_bar['value'] = i + 1
        p2.close()
        p2.join()
        ###################################################
        if islem['restock'] == 1:
            text_print(output_text, 'Restock işlemi yapılıyor...')
            main_excel = restock_files[0]
            restock(path, row_dataframe_dictionary, dataframe_dictionary, row_files, main_excel, columns_dict, maliyet_dict, save_name)
    try:
        main()
        text_print(output_text, 'İşlem başarıyla tamamlandı!', color='#90EE90')
    except:
        text_print(output_text, 'Beklenmeyen bir hata meydana geldi!', color='red')
        text_print(output_text, traceback.format_exc(), color='red')

def expration(username, password, tex: tkinter.Text, path, item_ids):
    def settings_creater():
        with open("Settings/expration_settings.txt", "w", encoding='utf-8') as file:
            file.write('login_button_id = mainForm:j_idt23, mainForm:j_idt13, mainForm:j_idt22\n'
                       'email_id = mainForm:email\n'
                       'password_id = mainForm:password\n'
                       'default_email = sales@buyable.net\n'
                       'default_password = hasali2603\n')
            file.close()
    def settings_reader():
        dictionary = {
            'login_button_id': [],
            'email_id': [],
            'password_id': [],
            'default_email': [],
            'default_password': [],
        }
        with open("Settings/expration_settings.txt", "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                line = line.split('=')
                if line[0] == 'login_button_id' or line[0] == 'login_button_id ':
                    degerler = line[1].split(',')
                    for deger in degerler:
                        deger = deger.replace('\n', '')
                        deger = deger.replace(' ', '', 1)
                        dictionary['login_button_id'].append(deger)
                if line[0] == 'email_id' or line[0] == 'email_id ':
                    degerler = line[1].split(',')
                    for deger in degerler:
                        deger = deger.replace('\n', '')
                        deger = deger.replace(' ', '', 1)
                        dictionary['email_id'].append(deger)
                if line[0] == 'password_id' or line[0] == 'password_id ':
                    degerler = line[1].split(',')
                    for deger in degerler:
                        deger = deger.replace('\n', '')
                        deger = deger.replace(' ', '', 1)
                        dictionary['password_id'].append(deger)
                if line[0] == 'default_email' or line[0] == 'default_email ':
                    degerler = line[1].split(',')
                    for deger in degerler:
                        deger = deger.replace('\n', '')
                        deger = deger.replace(' ', '', 1)
                        dictionary['default_email'].append(deger)
                if line[0] == 'default_password' or line[0] == 'default_password ':
                    degerler = line[1].split(',')
                    for deger in degerler:
                        deger = deger.replace('\n', '')
                        deger = deger.replace(' ', '', 1)
                        dictionary['default_password'].append(deger)
        return dictionary

    def login():

        url = "https://app.2dworkflow.com/login.jsf"
        session = requests.Session()
        response = session.get(url)
        main_dict = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        javax = soup.find('input', {'name': 'javax.faces.ViewState'})['value']
        button = soup.find('button')['name']
        payload = {'mainForm:email': username,
                   'mainForm:password': password,
                   'mainForm': 'mainForm',
                   'javax.faces.ViewState': javax,
                   button: ''}
        response = session.post(url, data=payload)
        if response.status_code == 200:
            text_print(tex, "Login Successful")
            id_list = []
            x = item_ids.split(',')
            for id in x:
                id = id.replace(' ', '')
                id_list.append(id)

            id_dict = {}
            shipments_url = "https://app.2dworkflow.com/shipped.jsf"
            response = session.get(shipments_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            tbody = soup.find("tbody", id="mainForm:shipments_data")
            fba_date = ""
            for id in id_list:
                main_dict[id] = {}
                href = ""


                if tbody:
                    trs = tbody.findAll("tr")
                    if trs:
                        for index, tr in enumerate(trs):
                            a = tr.find("a")
                            if a and id in a.get("title", ""):
                                href = a.get("href", "")
                                fba_date = trs[index-1].findAll("span")[2].text.split(",")[0]
                                print(fba_date)
                id_dict[id] = href
            for id in id_list:
                url_payload = 'https://app.2dworkflow.com/'
                response = session.get(f"{url_payload}{id_dict[id]}")
                print(id, f"{url_payload}{id_dict[id]}")
                soup = BeautifulSoup(response.text, 'html.parser')
                tbody = soup.find("tbody", {"id": "mainForm:shipmentItems_data"})
                tbody_info = soup.find("tbody", {"id": "mainForm:shipmentInfo_data"})
                info_tr = tbody_info.find("tr")
                trler = tbody.findAll("tr")
                shipment_name = ""
                tds = info_tr.findAll("td")
                shipment_name = tds[3].text
                print(shipment_name)

                for tr in trler:
                    sku = tr.find("span").text
                    main_dict[id][sku] = {}

                    main_dict[id][sku]["item_id"] = tr['data-rk']
                    main_dict[id][sku]["shipped"] = tr.findAll("td")[3].text
                    main_dict[id][sku]["created"] = fba_date
                    main_dict[id][sku]["shipment_name"] = shipment_name
                text_print(tex, f"{len(list(main_dict[id].keys()))} adet urun bulundu!")
                javax = soup.find('input', {'name': 'javax.faces.ViewState'})['value']

                for a, sku in enumerate(list(main_dict[id].keys())):
                    main_dict[id][sku]["date"] = []
                    text_print(tex, f"({id_list.index(id) + 1} / {len(id_list)}) {id}: {str(a+1)} / {str(len(list(main_dict[id].keys())))}")

                    payload = {
                        "mainForm": "mainForm",
                        'javax.faces.ViewState': javax,
                        'mainForm:shipmentItems_instantSelectedRowKey': main_dict[id][sku]["item_id"],
                        'mainForm:shipmentItems_selection': main_dict[id][sku]["item_id"],
                        'javax.faces.partial.ajax': 'true',
                        'javax.faces.source': 'mainForm:shipmentItems',
                        'javax.faces.partial.execute': 'mainForm:shipmentItems',
                        'javax.faces.partial.render': 'mainForm:boxContentsPanel mainForm:boxContents',
                        'javax.faces.partial.event': 'rowSelect',
                    }
                    response = session.post("https://app.2dworkflow.com/items.jsf", data=payload)
                    soup = BeautifulSoup(response.text, "lxml")
                    tbody = soup.find("tbody", {"id": "mainForm:boxContents_data"})
                    trler = tbody.findAll("tr")
                    if trler != None:
                        for tr in trler:
                            tdler = tr.findAll("td")
                            if tdler != None and len(tdler) > 3:
                                main_dict[id][sku]["date"].append(f" {tdler[3].text}")
                date_converter(main_dict, id)
                writer(main_dict, id)
            print("combined.xlsx dosyasi yazdiriliyor...")
            combined_writer(main_dict)
            print("combined.xlsx dosyasi basariyla yazdirildi")
            return main_dict
        else:
            print('giris basarisiz')
            return None

    def date_converter(main_dict, id):
        for sku in main_dict[id].keys():
            empty_list = []
            for date in main_dict[id][sku]["date"]:
                if date not in empty_list:
                    empty_list.append(date)
            main_dict[id][sku]["date"] = empty_list
            noktalidate = ''
            try:
                date = main_dict[id][sku]["date"][0]
                if '-' in date:
                    a = date.replace(' ', '')
                    x = a.split('-')
                    noktalidate = (x[1] + '.' + x[0] + '.' + x[2])
                elif '/' in date:
                    a = date.replace(' ', '')
                    x = a.split('/')
                    noktalidate = (x[1] + '.' + x[0] + '.' + x[2])
                elif '.' in date:
                    a = date.replace(' ', '')
                    x = a.split('.')
                    noktalidate = (x[1] + '.' + x[0] + '.' + x[2])
                elif date == []:
                    noktalidate = None
            except:
                noktalidate = None
            main_dict[id][sku]["noktali"] = noktalidate
    def writer(main_dictionary, id):
        save_name = f"{id}.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = save_name
        a = 2
        ws.cell(row=1, column=1).value = 'NAME'
        ws.cell(row=1, column=2).value = 'SHIPMENT ID'
        ws.cell(row=1, column=3).value = 'SHIPMENT DATE'
        ws.cell(row=1, column=4).value = 'SKU'
        ws.cell(row=1, column=5).value = 'SHIPPED'
        ws.cell(row=1, column=6).value = 'DATE'
        ws.cell(row=1, column=7).value = 'TR DATE'

        for sku in main_dictionary[id].keys():
            ws.cell(row=a, column=1).value = main_dictionary[id][sku]["shipment_name"]
            ws.cell(row=a, column=2).value = id
            ws.cell(row=a, column=3).value = main_dictionary[id][sku]["created"]
            ws.cell(row=a, column=4).value = sku
            ws.cell(row=a, column=5).value = main_dictionary[id][sku]["shipped"]
            ws.cell(row=a, column=6).value = main_dictionary[id][sku]["date"][0]
            ws.cell(row=a, column=7).value = main_dictionary[id][sku]["noktali"]
            c = 8
            for date in main_dictionary[id][sku]["date"][1:]:
                ws.cell(row=a, column=c).value = str(date)
                c = c + 1
            a = a + 1

        wb.save(f"{path}/{save_name}")
        text_print(tex, f"{id} {save_name} olarak belirtilen dizine kaydedildi!")


    def combined_writer(main_dictionary):
        save_name = f"combined.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = save_name

        a = 2
        for id in main_dictionary.keys():
            ws.cell(row=1, column=1).value = 'NAME'
            ws.cell(row=1, column=2).value = 'SHIPMENT ID'
            ws.cell(row=1, column=3).value = 'SHIPMENT DATE'
            ws.cell(row=1, column=4).value = 'SKU'
            ws.cell(row=1, column=5).value = 'SHIPPED'
            ws.cell(row=1, column=6).value = 'DATE'
            ws.cell(row=1, column=7).value = 'TR DATE'

            for sku in main_dictionary[id].keys():
                ws.cell(row=a, column=1).value = main_dictionary[id][sku]["shipment_name"]
                ws.cell(row=a, column=2).value = id
                ws.cell(row=a, column=3).value = main_dictionary[id][sku]["created"]
                ws.cell(row=a, column=4).value = sku
                ws.cell(row=a, column=5).value = main_dictionary[id][sku]["shipped"]
                ws.cell(row=a, column=6).value = main_dictionary[id][sku]["date"][0]
                ws.cell(row=a, column=7).value = main_dictionary[id][sku]["noktali"]
                c = 8
                for date in main_dictionary[id][sku]["date"][1:]:
                    ws.cell(row=a, column=c).value = str(date)
                    c = c + 1
                a = a + 1

        wb.save(f"{path}/{save_name}")
        text_print(tex, f"{id} {save_name} olarak belirtilen dizine kaydedildi!")

    def main():
        try:
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            if 'expration_settings.txt' not in os.listdir('Settings'):
                settings_creater()
            dictionary = settings_reader()
            text_print(tex, str(dictionary))
            main_dict = login()
            if main_dict:
                text_print(tex, "islem basariyla tamamlandi.", "green")
                open_folder_in_explorer(path)
            else:
                text_print(tex, "bir sorun meydana geldi!")
        except:
            text_print(tex, "bir hata meydana geldi! Hata kodu: ")
            e = traceback.format_exc()
            text_print(tex, e, "red")
    main()

def button(canvas2, button):
    canvas2.delete("all")
    canvas2.unbind_all("<MouseWheel>")
    window.unbind('<Configure>')
    silici(canvas, canvas2, window)
    scrollbar = Scrollbar()
    canvas2.config(scrollregion=canvas2.bbox("all"))  # Canvas'ın scroll bölgesini güncelle
    scrollbar.config(command=canvas2.yview)
    canvas2.config(yscrollcommand=scrollbar.set)
    canvas2.yview_moveto(0)

    image_dictionary = {
        button_1: program_icon_selected,
        button_2: program_icon_selected,
        button_3: program_icon_selected,
        button_4: program_icon_selected,
        button_5: home_icon_selected,
        button_6: program_icon_selected,
        button_7: program_icon_selected,
        button_8: program_icon_selected,
        button_9: program_icon_selected,
        button_10: program_icon_selected,
        button_11: program_icon_selected,
    }
    button_1.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_2.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_3.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_4.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_5.config(background=color, text_color=canvas2_text_color, image=home_icon_notselected)
    button_6.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_7.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_8.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_9.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_10.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button_11.config(background=color, text_color=canvas2_text_color, image=program_icon_notselected)
    button.config(background='#8AB4F8', text_color='black', image=image_dictionary[button])
    def dictionary_update(button):
        dictionary[button_1] = 0
        dictionary[button_2] = 0
        dictionary[button_3] = 0
        dictionary[button_4] = 0
        dictionary[button_5] = 0
        dictionary[button_6] = 0
        dictionary[button_7] = 0
        dictionary[button_8] = 0
        dictionary[button_9] = 0
        dictionary[button_10] = 0
        dictionary[button_11] = 0
        dictionary[button] = 1
    if button == button_1:
        dictionary_update(button_1)
        canvas2.unbind_all('<MouseWheel>')
        render_restock_view(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, resize_dictionary, active_dictionary, main_frame_resize)
    if button == button_2:
        window.unbind("<Configure>")
        dictionary_update(button_2)
        shipmentCreater(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, main_frame_resize, resize_dictionary)
    if button == button_3:
        dictionary_update(button_3)
        canvas2.unbind_all('<MouseWheel>')
        render_tsv_view(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, main_frame_resize)
    if button == button_4:
        dictionary_update(button_4)
        canvas2.config(height=window.winfo_height())
        render_restock_view(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, resize_dictionary, active_dictionary, main_frame_resize)
    if button == button_5:
        dictionary_update(button_5)
        canvas2.unbind_all('<MouseWheel>')

        anasayfa_canvas = Canvas(
            canvas2,
            background=color,
            highlightthickness=0,
            border=0
        )
        anasayfa_canvas.pack(anchor='center', expand=True, side=LEFT)

        line = Frame(
            anasayfa_canvas,
            height=4,
            background=line_color
        )

        hello = Label(
            anasayfa_canvas,
            background=color,
            fg=canvas2_text_color,
            text="KWIEK LLC TOPLU İŞLEM PLATFORMUNA HOŞGELDİNİZ!",
            font=("JetBrainsMonoRoman Regular", 24 * -1)
        )

        islem = Label(
            anasayfa_canvas,
            background=color,
            text="Bir işlem yapmak için lütfen sol menüdeki işlemlerden birini seçiniz...",
            fg=canvas2_text_color,
            font=("JetBrainsMonoRoman Regular", 15 * -1)
        )

        hello.grid(column=0, row=0, sticky='ew', padx=40)
        line.grid(column=0, row=1, sticky='ew', pady=15)
        islem.grid(column=0, row=2, sticky='ew')
        liste= [canvas, canvas2, button_1, button_2, button_3, button_4, button_5]
        window.bind("<Configure>", lambda e: main_resize(e,liste, hello, islem))
    if button == button_6:

        dictionary_update(button_6)
        canvas2.unbind_all('<MouseWheel>')
        render_invoice_view(canvas, canvas2, main_frame_resize, window, color, line_color, canvas2_text_color, dosyalar_dictionary,
                    selected_image, not_selected_image, csv_drag_drop_image, csv_icon_image)
    if button == button_7:
        dictionary_update(button_7)
        render_converter_view(canvas, canvas2, main_frame_resize, window, color, line_color, canvas2_text_color, dosyalar_dictionary)
    if button == button_8:
        dictionary_update(button_8)
        render_costupdater_view(canvas, canvas2, window, color, line_color, canvas2_text_color, dosyalar_dictionary, main_frame_resize)
    if button == button_9:
        dictionary_update(button_9)
        render_updater_view(canvas2, color, window, line_color, canvas2_text_color, CURRENT_VERSION, is_connected)
    if button == button_10:
        dictionary_update(button_10)
        render_invoicefinder_view(canvas, canvas2, main_frame_resize, window, color, line_color, canvas2_text_color, dosyalar_dictionary)
    if button == button_11:
        dictionary_update(button_11)
        render_ordercreate_view(canvas, canvas2, main_frame_resize, window, color, line_color, canvas2_text_color, dosyalar_dictionary, resize_dictionary)

def is_connected_whenstart():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        api_url = "https://api.github.com/repos/hasali2603/KWIEKLLC/releases/latest"
        response = requests.get(api_url)
        release_data = response.json()
        latest_version = release_data['tag_name']
        if latest_version > CURRENT_VERSION:
            version.config(text=f"{CURRENT_VERSION} yeni version({latest_version}) mevcut!", fg='yellow')
            tk.messagebox.showinfo("Version", f"New version available: {latest_version}!")
    except:
        pass

def is_connected(CURRENT_VERSION, progress_bar, progress_label, doyouwanna_frame, label, yuklebutton, releasebutton):

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        application_updater(CURRENT_VERSION, progress_bar, progress_label, doyouwanna_frame, label, yuklebutton, releasebutton)
    except OSError:
        messagebox.showwarning("Uyarı", "İnternet bağlantınızı kontrol edip daha sonra tekrar deneyin.")

def download_file_with_progress(url, save_path, progress_bar, progress_label):
    response = requests.head(url, allow_redirects=True)
    total_size = int(response.headers.get('content-length', 0))
    progress_bar.pack(side=BOTTOM, fill=X)
    progress_label.pack(side=BOTTOM, anchor='w')
    progress_bar['maximum'] = total_size
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as file:
        downloaded_size = 0
        for chunk in response.iter_content(1024):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
                progress_bar['value'] = downloaded_size
                window.update_idletasks()

def start_download(url, progress_bar, progress_label):
    temp_dir = tempfile.gettempdir()
    update_save_path = os.path.join(temp_dir, "KWIEKLLC_update.exe")
    download_file_with_progress(url, update_save_path, progress_bar, progress_label)

def application_updater(CURRENT_VERSION, progress_bar, progress_label, doyouwanna_frame, label:tk.Label, yuklebutton, releasebutton):
    def baslat_click(e,c,t, i):
        i.config(background=c, text_color=t)
        update_starter()
    def release_click(e,c,t,i,text, vs):
        i.config(background=c, text_color=t)
        release_window = Tk()
        release_window.geometry("500x300")
        release_window.title(f'Release Notes of {vs}')
        releasenotes_text = Text(
            release_window,
            border=0,
            wrap= WORD,
            bg=line_color,
            fg='#c0c0c0',
            #height = int(settings_height/15),
            font=("JetBrainsMonoRoman Regular", 10),
            insertbackground='#c0c0c0'
        )
        releasenotes_text.insert(tk.END, text)
        releasenotes_text.see(tk.END)
        releasenotes_text.config(state=tk.DISABLED)
        releasenotes_text.pack(side=LEFT, fill=BOTH, expand=True, anchor='nw')
    def update_starter():
        t = Thread(target=update, daemon=True)
        t.start()
    def update():
        asset_url = release_data['assets'][1]['browser_download_url']
        start_download(asset_url, progress_bar, progress_label)
        temp_dir = tempfile.gettempdir()
        batch_file_path = os.path.join(temp_dir, "run_update.bat")
        with open(batch_file_path, "w") as batch_file:
            batch_file.write(
                f'@echo off\n'
                f'set "update_path=%~dp0KWIEKLLC_update.exe"\n'
                f'start "" /b "%update_path%"\n'
                f':wait_loop\n'
                f'tasklist /FI "IMAGENAME eq KWIEKLLC_update.exe" 2>NUL | find /I /N "KWIEKLLC_update.exe">NUL\n'
                f'if "%ERRORLEVEL%"=="0" (\n'
                f'    timeout /t 5 > NUL\n'
                f'    goto wait_loop\n'
                f')\n'
                f'echo Update process finished >> "%~dp0update_log.txt"\n'
                f'echo Update process finished >> "%~dp0update_log.txt"\n'
                f'del /f /q "%~dp0KWIEKLLC_update.exe"\n'
                f'del /f /q "%~f0" & exit\n'
            )

        # Run the batch file
        subprocess.Popen([batch_file_path], creationflags=subprocess.CREATE_NO_WINDOW)
        exit()
    def force_exit():
        subprocess.run(["taskkill", "/F", "/IM", "KWIEK LLC.exe"])
        sys.exit()
    def exit():
        os._exit(0)
        window.quit()
        try:
            force_exit()
        except:
            pass
        pid = os.getpid()  # Geçerli işlem kimliğini alır
        os.kill(pid, signal.SIGTERM)  # İşlemi zorla sonlandırır
        sys.exit()



    api_url = "https://api.github.com/repos/hasali2603/KWIEKLLC/releases/latest"

    response = requests.get(api_url) #headers=headers)
    release_data = response.json()
    latest_version = release_data['tag_name']
    if latest_version > CURRENT_VERSION:
        release_notes = release_data['body']
        version.config(text=f"{CURRENT_VERSION} yeni version({latest_version}) mevcut!", fg='yellow')

        label.config(text=f'Yeni bir versiyon bulundu({latest_version})! Yüklemek istiyor musun?')

        yuklebutton.bind("<Button-1>", lambda e: baslat_click(e,'#8AB4F8','black', yuklebutton))
        releasebutton.bind("<Button-1>", lambda e: release_click(e,'#8AB4F8','black', releasebutton, release_notes, latest_version))

        doyouwanna_frame.grid(column=0, row=2, sticky='w')
    else:
        items = doyouwanna_frame.winfo_children()
        for item in items:
            if type(item) == Label:
                item.config(text='Uygulama güncel!')
            else:
                item.grid_forget()
        doyouwanna_frame.grid(column=0, row=2, sticky='w')

if __name__ == '__main__':
    freeze_support()

    CURRENT_VERSION = "v1.2.2"

    OUTPUT_PATH = Path(__file__).resolve().parent
    ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


    dosyalar_dictionary = {}

    color = '#202124'
    window = TkinterDnD.Tk()

    #bg='#ADD8E6'

    canvas2_text_color = '#E3E3E3'
    line_color='#3F4042'
    active_dictionary= {
        'restock': 1,
        'export': 1
    }

    #865x519
    wr=float(865/1920)
    hr=float(519/1080)
    m = get_monitors()[0]

    scale = 1
    window.configure(bg = color)
    screenwidth = int(scale*wr * 2560)
    screen_height = int(scale*hr * 1600)
    #print(screenwidth,screen_height)
    window.geometry("{}x{}".format(screenwidth, screen_height))
    window.title('KWIEK LLC')
    try:
        dark_title_bar(window)
    except:pass
    try:
        window.iconbitmap('assets/icon.ico')
    except:pass

    original_selected_image = HASAN.open(relative_to_assets('selected.png'))
    original_notselected_image = HASAN.open(relative_to_assets('not_selected.png'))
    selected_resized_image = original_selected_image.resize((15, 15))
    notselected_resized_image = original_notselected_image.resize((15, 15))
    selected_image = ImageTk.PhotoImage(selected_resized_image)
    not_selected_image = ImageTk.PhotoImage(notselected_resized_image)
    csv_drag_drop_image = PhotoImage(file=relative_to_assets('csv_drag_drop_rs.png'))
    csv_icon_image = PhotoImage(file=relative_to_assets('csv_icon_rs.png'))
    txt_drag_drop_image = PhotoImage(file=relative_to_assets('txt_drag_drop_rs.png'))
    txt_icon_image = PhotoImage(file=relative_to_assets('txt_icon_rs.png'))
    
    costupdater_settings_var = (
        'cost = cost\n'
        'sku = sku\n'
        'additional cost = additional_cost\n'
        'business pricing = business_pricing\n'
        'bp strategy = bp_strategy\n'
        'qd strategy = qd_strategy\n'
        '====================================\n'
        'BX: 0.3\n'
        'CANDY: 0.3\n'
        'COS: 0.3\n'
        'CS: 0.3\n'
        'CSC: 0.3\n'
        'DL: 0.3\n'
        'FC: 0.3\n'
        'FD: 0.3\n'
        'FL: 0.75\n'
        'FOUR: 0.3\n'
        'FR: 0.3\n'
        'GEMCO: 0.3\n'
        'IL: 0.75\n'
        'JC: 0.3\n'
        'KH: 0.3\n'
        'LR: 0.3\n'
        'MD: 0.75\n'
        'MONIN PUMP SL: 0.3\n'
        'NC: 0.3\n'
        'NF: 0.3\n'
        'NJ: 0.3\n'
        'NK: 0.3\n'
        'NT: 0.3\n'
        'SN: 0.3\n'
        'UC: 0.3\n'
        'UD: 0.3\n'
        'UN: 0.3\n'
        'UPC: 0.3\n'
        'WB: 0.3\n'
        'WEBS: 0.3\n'
    )





    global last_scale
    last_scale = 1
    def main_frame_resize():
        global last_scale
        new_width = window.winfo_width()
        new_height = window.winfo_height()
        scale = (new_width*new_height)/(screen_height*screenwidth)
        scale = round(scale,1)
        if scale <= 1:
            scale = 1
        elif scale >= 1.60:
            scale = 1.60
        canvas.place_configure(height=new_height)
        canvas2.place_configure(height=new_height, width=new_width-canvas.winfo_width()+10)
        if scale != last_scale:
            canvas.place_configure(width=resize_dictionary[canvas]['width']*scale)
            canvas2.place_configure(x=resize_dictionary[canvas2]['x']*scale, y=resize_dictionary[canvas2]['y']*scale)
            button_list=[button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8, button_9, button_10, button_11]
            for button in button_list:
                width = resize_dictionary[button]['width']*scale
                height = resize_dictionary[button]['height']*scale
                button.config(width=width, height=height, round=20*scale)
            last_scale = scale
        return scale

    def main_resize(event, liste, hello, islem):
        scale = main_frame_resize()
        hello.config(font=("JetBrainsMonoRoman Regular", round(24*scale)*-1))
        islem.config(font=("JetBrainsMonoRoman Regular", round(15*scale)*-1))
    window.update()

    canvas2_height = 519
    canvas2_width = 763
    canvas_widht = 175
    canvas2 = Canvas(
        window,
        height = int((window.winfo_height())),
        width = int((window.winfo_width()-canvas_widht)),
        bd = 0,
        highlightthickness = 0,
        relief = "ridge",
        background=color
    )
    canvas2.place(x = int(canvas_widht*scale), y = 0)

    canvas2.pack_propagate(False)
    canvas = Canvas(
        window,
        bg = "#FFFFFF",
        height = int((window.winfo_height())),
        width = int(canvas_widht*scale)+3,
        border=0,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge",
        background=color
    )
    canvas.place(x = 0, y = 0)
    canvas.grid_propagate(False)
    canvas.grid_columnconfigure(0, weight=1)
    canvas.grid_columnconfigure(1, weight=2)

    anasayfa_canvas = Canvas(
        canvas2,
        background=color,
        highlightthickness=0,
        border=0
    )
    anasayfa_canvas.pack(anchor='center', expand=True, side=LEFT)

    line = Frame(
        anasayfa_canvas,
        height=4,
        background=line_color
    )

    hello = Label(
        anasayfa_canvas,
        background=color,
        fg=canvas2_text_color,
        text="KWIEK LLC TOPLU İŞLEM PLATFORMUNA HOŞGELDİNİZ!",
        font=("JetBrainsMonoRoman Regular", 24 * -1)
    )

    islem = Label(
        anasayfa_canvas,
        background=color,
        text="Bir işlem yapmak için lütfen sol menüdeki işlemlerden birini seçiniz...",
        fg=canvas2_text_color,
        font=("JetBrainsMonoRoman Regular", 15 * -1)
    )

    hello.grid(column=0, row=0, sticky='ew', padx=40)
    line.grid(column=0, row=1, sticky='ew', pady=15)
    islem.grid(column=0, row=2, sticky='ew')

    home_icon_selected = PhotoImage(file=relative_to_assets('home_icon_selected_rs.png'))
    home_icon_hover = PhotoImage(file=relative_to_assets('home_icon_hover_rs.png'))
    home_icon_notselected = PhotoImage(file=relative_to_assets('home_icon_notselected_rs.png'))
    program_icon_selected = PhotoImage(file=relative_to_assets('program_icon_selected_rs.png'))
    program_icon_hover = PhotoImage(file=relative_to_assets('program_icon_hover_rs.png'))
    program_icon_notselected = PhotoImage(file=relative_to_assets('program_icon_notselected_rs.png'))
    pad = 5
    button_1 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Expration Date",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_1.grid(column=0, row=6)

    button_1.bind('<Enter>', lambda event: button_hover(event, button_1, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_1.bind('<Leave>', lambda event: button_leave(event, button_1, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_1.bind("<Button-1>", lambda e: button(canvas2, button_1))
    button_1_line = Frame(canvas, height=2, bg=line_color)
    button_1_line.grid(column=0, row=7, sticky='ew')
    button_2 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Shipment Creater",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_2.grid(column=0, row=8)
    button_2.bind('<Enter>', lambda event: button_hover(event, button_2, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_2.bind('<Leave>', lambda event: button_leave(event, button_2, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_2.bind("<Button-1>", lambda e: button(canvas2, button_2))
    button_2_line = Frame(canvas, height=2, bg=line_color)
    button_2_line.grid(column=0, row=9, sticky='ew')
    button_3 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="TSV PROGRAMI",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_3.grid(column=0, row=10)
    button_3.bind('<Enter>', lambda event: button_hover(event, button_3, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_3.bind('<Leave>', lambda event: button_leave(event, button_3, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_3.bind("<Button-1>", lambda e: button(canvas2, button_3))
    button_3_line = Frame(canvas, height=2, bg=line_color)
    button_4 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="RESTOCK",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_4.grid(column=0, row=4)
    button_4.bind('<Enter>', lambda event: button_hover(event, button_4, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_4.bind('<Leave>', lambda event: button_leave(event, button_4, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_4.bind("<Button-1>", lambda e: button(canvas2, button_4))
    button_4_line = Frame(canvas, height=2, bg=line_color)
    button_4_line.grid(column=0, row=5, sticky='ew')

    button_5 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color='black',
        text="Ana Sayfa",
        align_text="west",
        round=20,
        background='#8AB4F8',
        corners=[0,1,0,1],
        image=home_icon_selected,
        text_pad=pad
    )
    button_5.grid(column=0, row=0, pady=(30,0))
    button_5.bind('<Enter>', lambda event: button_hover(event, button_5, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_5.bind('<Leave>', lambda event: button_leave(event, button_5, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_5.bind("<Button-1>", lambda e: button(canvas2, button_5))
    button_5_line1 = Frame(canvas, height=2, bg=line_color)
    button_5_line2 = Frame(canvas, height=2, bg=line_color)
    button_5_line3 = Frame(canvas, height=2, bg=line_color)
    button_5_line1.grid(column=0, row=1, sticky='ew', pady=(20, 1))
    button_5_line2.grid(column=0, row=2, sticky='ew', pady=(1, 1))
    button_5_line3.grid(column=0, row=3, sticky='ew', pady=(1, 20))

    button_6_line = Frame(canvas, height=2, bg=line_color)
    button_6_line.grid(column=0, row=11, sticky='ew')
    button_6 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Invoice",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_6.grid(column=0, row=12)
    button_6.bind('<Enter>', lambda event: button_hover(event, button_6, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_6.bind('<Leave>', lambda event: button_leave(event, button_6, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_6.bind("<Button-1>", lambda e: button(canvas2, button_6))

    button_7_line = Frame(canvas, height=2, bg=line_color)
    button_7_line.grid(column=0, row=13, sticky='ew')
    button_7 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Converter",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_7.grid(column=0, row=14)
    button_7.bind('<Enter>', lambda event: button_hover(event, button_7, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_7.bind('<Leave>', lambda event: button_leave(event, button_7, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_7.bind("<Button-1>", lambda e: button(canvas2, button_7))

    button_8_line = Frame(canvas, height=2, bg=line_color)
    button_8_line.grid(column=0, row=15, sticky='ew')

    button_8 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Cost Updater",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_8.grid(column=0, row=16)
    button_8.bind('<Enter>', lambda event: button_hover(event, button_8, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_8.bind('<Leave>', lambda event: button_leave(event, button_8, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_8.bind("<Button-1>", lambda e: button(canvas2, button_8))

    button_9_line = Frame(canvas, height=2, bg=line_color)
    button_9_line.grid(column=0, row=21, sticky='ew')
    button_9 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Update",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_9.grid(column=0, row=22)
    button_9.bind('<Enter>', lambda event: button_hover(event, button_9, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_9.bind('<Leave>', lambda event: button_leave(event, button_9, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_9.bind("<Button-1>", lambda e: button(canvas2, button_9))

    button_10_line = Frame(canvas, height=2, bg=line_color)
    button_10_line.grid(column=0, row=17, sticky='ew')
    button_10 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Invoice Finder",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_10.grid(column=0, row=18)
    button_10.bind('<Enter>', lambda event: button_hover(event, button_10, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_10.bind('<Leave>', lambda event: button_leave(event, button_10, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_10.bind("<Button-1>", lambda e: button(canvas2, button_10))

    button_11_line = Frame(canvas, height=2, bg=line_color)
    button_11_line.grid(column=0, row=19, sticky='ew')
    button_11 = MyButton(
        canvas,
        width=canvas_widht,
        height=45,
        text_color=canvas2_text_color,
        text="Order Create",
        align_text="west",
        round=20,
        background=color,
        corners=[0,1,0,1],
        image=program_icon_notselected,
        text_pad=pad
    )
    button_11.grid(column=0, row=20)
    button_11.bind('<Enter>', lambda event: button_hover(event, button_11, dictionary, button_5, program_icon_hover, home_icon_hover))
    button_11.bind('<Leave>', lambda event: button_leave(event, button_11, dictionary, color, button_5, program_icon_notselected, home_icon_notselected))
    button_11.bind("<Button-1>", lambda e: button(canvas2, button_11))
    dictionary = {
        button_1: 0,
        button_2: 0,
        button_3: 0,
        button_4: 0,
        button_5: 1,
        button_6: 0,
        button_7: 0,
        button_8: 0,
        button_9: 0,
        button_10: 0,
        button_11: 0,
    }
    version = Label(canvas, fg=canvas2_text_color, bg=color, text=CURRENT_VERSION, font=('Helvatica', 8))
    version.place(x=0, y=0)
    window.after(1, is_connected_whenstart)
    liste = [canvas, canvas2, button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8]

    window.update_idletasks()
    resize_dictionary = {
        canvas: {'width': canvas.winfo_width(), 'height': canvas.winfo_height(), 'x': canvas.winfo_x(), 'y': canvas.winfo_y()},
        canvas2: {'width': canvas2.winfo_width(), 'height': canvas2.winfo_height(), 'x': canvas2.winfo_x(), 'y': canvas2.winfo_y()},
        button_1: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_1.winfo_x(), 'y': button_1.winfo_y()},
        button_2: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_2.winfo_x(), 'y': button_2.winfo_y()},
        button_3: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_3.winfo_x(), 'y': button_3.winfo_y()},
        button_4: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_4.winfo_x(), 'y': button_4.winfo_y()},
        button_5: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_5.winfo_x(), 'y': button_5.winfo_y()},
        button_6: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_6.winfo_x(), 'y': button_6.winfo_y()},
        button_7: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_7.winfo_x(), 'y': button_7.winfo_y()},
        button_8: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_8.winfo_x(), 'y': button_8.winfo_y()},
        button_9: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_9.winfo_x(), 'y': button_9.winfo_y()},
        button_10: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_10.winfo_x(), 'y': button_10.winfo_y()},
        button_11: {'width': canvas_widht*scale, 'height': 45*scale, 'x': button_11.winfo_x(), 'y': button_11.winfo_y()},
    }
    window.bind('<Configure>', lambda e: main_resize(e, liste, hello, islem))
    #888888
    window.mainloop()


