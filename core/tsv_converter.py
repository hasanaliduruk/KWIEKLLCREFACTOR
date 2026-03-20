import csv
import os
import openpyxl
from xlsxwriter import Workbook

def convert_tsv_to_excel(file_path: str, target_path: str, target_name: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Hata: Belirtilen dosya bulunamadı -> {file_path}")
    
    if target_name == '' or target_name == ' ' or target_name is None:
        target_name = "Converted_File"
        
    if not target_name.endswith('.xlsx'):
        target_name += '.xlsx'
        
    os.makedirs(target_path, exist_ok=True)
    full_target_path = os.path.join(target_path, target_name)
    
    try:
        workbook = Workbook(full_target_path)
        worksheet = workbook.add_worksheet()
        
        with open(file_path, 'rt', encoding='utf8') as f:
            reader = csv.reader(f, delimiter='\t')
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()
        
        wb = openpyxl.load_workbook(full_target_path)
        sheet = wb.active
        for column_cells in sheet.columns:
            length = max(len(str(cell.value) or "") for cell in column_cells)
            sheet.column_dimensions[openpyxl.utils.get_column_letter(column_cells[0].column)].width = length + 3
        wb.save(full_target_path)
        
        return {
            "status": "success",
            "message": "Conversion Completed Successfully.",
            "output_path": full_target_path
        }
        
    except Exception as e:
        raise RuntimeError(f"Dönüştürme sırasında mantıksal bir hata oluştu: {str(e)}")