"""Add New Title to a flat .xlsx export without rewriting its existing cells."""

from __future__ import annotations

from copy import copy
from pathlib import Path
import os
import re
import shutil
import tempfile
from typing import Callable
from zipfile import ZipFile

from lxml import etree
from openpyxl.utils import column_index_from_string, get_column_letter


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
CELL_REF = re.compile(r"^([A-Z]+)([1-9]\d*)$")
CELL_FORMULA_REF = re.compile(r"(?<![A-Za-z0-9_])\$?[A-Z]{1,3}\$?[1-9]\d*(?!\w|\s*\()", re.I)
QUOTED_FORMULA_TEXT = re.compile(r'"(?:[^"]|"")*"')
SHEET_PART = re.compile(r"^xl/worksheets/sheet\d+\.xml$")
UNSUPPORTED_SHEET_TAGS = {
    NS + tag for tag in (
        "mergeCells", "conditionalFormatting", "dataValidations", "tableParts",
        "drawing", "legacyDrawing", "extLst", "hyperlinks",
    )
}


def _shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    values = []
    with archive.open("xl/sharedStrings.xml") as stream:
        for _, element in etree.iterparse(stream, events=("end",), tag=NS + "si", huge_tree=True):
            values.append("".join(element.itertext()))
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]
    return values


def _cell_text(cell, shared_strings: list[str]) -> str:
    if cell is None:
        return ""
    if cell.find(NS + "f") is not None:
        raise ValueError("Title veya Brand sütununda formül bulunuyor; metin değeri gerekli.")
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        inline = cell.find(NS + "is")
        return "".join(inline.itertext()) if inline is not None else ""
    value = cell.findtext(NS + "v")
    if cell_type == "s" and value is not None:
        return shared_strings[int(value)]
    return value or ""


def _column_number(cell) -> int:
    match = CELL_REF.match(cell.get("r", ""))
    if not match:
        raise ValueError("Excel hücre adresi okunamadı.")
    return column_index_from_string(match.group(1))


def _headers(archive: ZipFile, sheet_part: str, shared_strings: list[str]) -> tuple[int, int | None, bool]:
    with archive.open(sheet_part) as stream:
        for _, row in etree.iterparse(stream, events=("end",), tag=NS + "row", huge_tree=True):
            if row.get("r") != "1":
                raise ValueError("Title başlığı Excel'in ilk satırında olmalı.")
            cells = [child for child in row if child.tag == NS + "c"]
            labels = {_cell_text(cell, shared_strings).strip().casefold(): _column_number(cell) for cell in cells}
            title_columns = [_column_number(cell) for cell in cells if _cell_text(cell, shared_strings).strip().casefold() == "title"]
            if len(title_columns) != 1:
                raise ValueError("İlk satırda tek bir Title sütunu bulunmalı.")
            new_title_columns = [_column_number(cell) for cell in cells if _cell_text(cell, shared_strings).strip().casefold() == "new title"]
            if new_title_columns and new_title_columns != [title_columns[0] + 1]:
                raise ValueError("New Title sütunu Title'ın hemen yanında ve tek olmalı.")
            return title_columns[0], labels.get("brand"), bool(new_title_columns)
    raise ValueError("Excel sayfası boş.")


def _shift_range(ref: str, inserted_column: int) -> str:
    def shift_coordinate(coordinate: str) -> str:
        match = CELL_REF.match(coordinate)
        if not match:
            return coordinate
        column = column_index_from_string(match.group(1))
        if column >= inserted_column:
            column += 1
        return get_column_letter(column) + match.group(2)

    return ":".join(shift_coordinate(part) for part in ref.split(":"))


def _update_columns(element, title_column: int):
    inserted_column = title_column + 1
    title_definition = None
    for column in element:
        if column.tag != NS + "col":
            continue
        low = int(column.get("min", "1"))
        high = int(column.get("max", str(low)))
        if low <= title_column <= high:
            title_definition = column
        if low >= inserted_column:
            column.set("min", str(low + 1))
            column.set("max", str(high + 1))
        elif high >= inserted_column:
            column.set("max", str(high + 1))
    if title_definition is not None and int(title_definition.get("max", "0")) == title_column:
        duplicate = copy(title_definition)
        duplicate.set("min", str(inserted_column))
        duplicate.set("max", str(inserted_column))
        element.insert(list(element).index(title_definition) + 1, duplicate)


def _new_inline_cell(address: str, value: str, source_cell=None):
    attributes = {"r": address, "t": "inlineStr"}
    if source_cell is not None and source_cell.get("s") is not None:
        attributes["s"] = source_cell.get("s")
    cell = etree.Element(NS + "c", attributes)
    inline = etree.SubElement(cell, NS + "is")
    text = etree.SubElement(inline, NS + "t")
    text.text = value
    return cell


def _process_row(row, title_column: int, brand_column: int | None, existing_new_title: bool, shared_strings, cleaner, stats):
    row_number = int(row.get("r", "0"))
    existing_cells = [child for child in row if child.tag == NS + "c"]
    original_columns = {_column_number(cell): cell for cell in existing_cells}
    title_cell = original_columns.get(title_column)
    brand_cell = original_columns.get(brand_column) if brand_column is not None else None
    previous_new_title_cell = original_columns.get(title_column + 1) if existing_new_title else None
    if row_number == 1:
        new_text = "New Title"
    else:
        original_title = _cell_text(title_cell, shared_strings).strip()
        brand = _cell_text(brand_cell, shared_strings).strip()
        new_text = cleaner(original_title, brand) if original_title else ""
        stats["rows"] += 1
        if not original_title:
            stats["blank"] += 1
        elif new_text != original_title:
            stats["changed"] += 1
        if original_title and not new_text:
            stats["no_identity"] += 1

    for cell in existing_cells:
        if cell is previous_new_title_cell:
            row.remove(cell)
            continue
        formula = cell.find(NS + "f")
        if formula is not None:
            formula_without_strings = QUOTED_FORMULA_TEXT.sub("", formula.text or "")
            if CELL_FORMULA_REF.search(formula_without_strings) or re.search(r"\b(?:INDIRECT|OFFSET|ADDRESS)\s*\(", formula.text or "", re.I):
                raise ValueError("Hücre başvurulu formüller içeren dosyalar henüz desteklenmiyor.")
        column = _column_number(cell)
        if not existing_new_title and column > title_column:
            cell.set("r", get_column_letter(column + 1) + str(row_number))

    if new_text or row_number == 1:
        new_cell = _new_inline_cell(
            get_column_letter(title_column + 1) + str(row_number), new_text,
            previous_new_title_cell if previous_new_title_cell is not None else title_cell,
        )
        insert_position = next(
            (index for index, child in enumerate(row) if child.tag == NS + "c" and _column_number(child) > title_column + 1),
            len(row),
        )
        row.insert(insert_position, new_cell)

    if not existing_new_title and "spans" in row.attrib:
        lower, upper = row.get("spans").split(":")
        if int(upper) >= title_column + 1:
            row.set("spans", f"{lower}:{int(upper) + 1}")


def _rewrite_sheet(source_stream, target_stream, title_column, brand_column, existing_new_title, shared_strings, cleaner, progress_callback, stats):
    parser = etree.iterparse(source_stream, events=("start", "end"), huge_tree=True)
    with etree.xmlfile(target_stream, encoding="UTF-8") as writer:
        writer.write_declaration(standalone=True)
        root_context = None
        data_context = None
        root = None
        for event, element in parser:
            if event == "start" and root is None:
                root = element
                root_context = writer.element(root.tag, root.attrib, nsmap=root.nsmap)
                root_context.__enter__()
                continue
            if event == "start" and element.tag == NS + "sheetData":
                data_context = writer.element(element.tag, element.attrib)
                data_context.__enter__()
                continue
            if event != "end":
                continue
            if element.tag == NS + "row" and data_context is not None:
                _process_row(element, title_column, brand_column, existing_new_title, shared_strings, cleaner, stats)
                writer.write(element)
                element.clear()
                while element.getprevious() is not None:
                    del element.getparent()[0]
                if progress_callback and stats["rows"] and stats["rows"] % 2000 == 0:
                    progress_callback(f"{stats['rows']:,} satır işlendi...")
            elif element.tag == NS + "sheetData":
                data_context.__exit__(None, None, None)
                data_context = None
                element.clear()
                root.remove(element)
            elif element.getparent() is root:
                if element.tag in UNSUPPORTED_SHEET_TAGS:
                    raise ValueError("Bu Excel dosyasında karmaşık sayfa öğeleri bulunuyor; dışa aktarım desteklenmiyor.")
                if element.tag == NS + "cols" and not existing_new_title:
                    _update_columns(element, title_column)
                elif element.tag == NS + "dimension" and not existing_new_title and element.get("ref"):
                    element.set("ref", _shift_range(element.get("ref"), title_column + 1))
                elif element.tag == NS + "autoFilter" and not existing_new_title and element.get("ref"):
                    element.set("ref", _shift_range(element.get("ref"), title_column + 1))
                writer.write(element)
                element.clear()
                root.remove(element)
            elif element is root:
                root_context.__exit__(None, None, None)


def _unique_output_path(source_file: Path, output_folder: Path) -> Path:
    base = source_file.stem + "_new_titles"
    candidate = output_folder / f"{base}.xlsx"
    suffix = 2
    while candidate.exists() or candidate.resolve() == source_file.resolve():
        candidate = output_folder / f"{base}_{suffix}.xlsx"
        suffix += 1
    return candidate


def process_title_cleaner(
    input_file: str,
    output_folder: str | None,
    cleaner: Callable[[str, str], str],
    progress_callback: Callable[[str], None] | None = None,
    override_original: bool = False,
) -> dict:
    """Update New Title in a new file or atomically replace the source workbook."""
    source_file = Path(input_file)
    destination_folder = source_file.parent if override_original else Path(output_folder or "")
    if source_file.suffix.lower() != ".xlsx" or not source_file.is_file():
        raise ValueError("Geçerli bir .xlsx dosyası seçin.")
    if not override_original and (not output_folder or not destination_folder.is_dir()):
        raise ValueError("Geçerli bir çıktı klasörü seçin.")

    stats = {"rows": 0, "changed": 0, "blank": 0, "no_identity": 0}
    temp_path = None
    try:
        with ZipFile(source_file) as source_archive:
            parts = [name for name in source_archive.namelist() if SHEET_PART.match(name)]
            if len(parts) != 1:
                raise ValueError("Tek sayfalı bir ürün Excel dosyası seçin.")
            if any(name.startswith((
                "xl/drawings/", "xl/charts/", "xl/tables/", "xl/pivotTables/",
                "xl/worksheets/_rels/", "xl/externalLinks/",
            )) for name in source_archive.namelist()):
                raise ValueError("Bu dosyada çizim, tablo veya pivot var; bu dışa aktarım biçimi desteklenmiyor.")
            if progress_callback:
                progress_callback("Excel dosyası açıldı; sütunlar okunuyor...")
            shared_strings = _shared_strings(source_archive)
            sheet_part = parts[0]
            title_column, brand_column, existing_new_title = _headers(source_archive, sheet_part, shared_strings)
            if progress_callback:
                progress_callback(
                    f"Sütunlar doğrulandı: Title {get_column_letter(title_column)}, "
                    f"New Title {get_column_letter(title_column + 1)}"
                    + (f", Brand {get_column_letter(brand_column)}." if brand_column else ".")
                )
                progress_callback(
                    "Var olan New Title sütunu yeniden hesaplanıyor..."
                    if existing_new_title else "Title yanına New Title sütunu ekleniyor..."
                )

            with tempfile.NamedTemporaryFile(prefix="title_cleaner_", suffix=".xlsx", dir=destination_folder, delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            with ZipFile(temp_path, "w") as output_archive:
                for part in source_archive.infolist():
                    part_copy = copy(part)
                    with source_archive.open(part) as source_stream:
                        with output_archive.open(part_copy, "w", force_zip64=True) as output_stream:
                            if part.filename == sheet_part:
                                _rewrite_sheet(
                                    source_stream, output_stream, title_column, brand_column, existing_new_title,
                                    shared_strings, cleaner, progress_callback, stats,
                                )
                            else:
                                shutil.copyfileobj(source_stream, output_stream, length=1024 * 1024)

        final_path = source_file if override_original else _unique_output_path(source_file, destination_folder)
        if progress_callback:
            progress_callback(f"Temizleme bitti: {stats['rows']:,} satır tarandı. Excel dosyası kaydediliyor...")
            if override_original:
                progress_callback("Kaynak dosya güvenli biçimde güncelleniyor...")
        if override_original:
            with ZipFile(temp_path) as check_archive:
                bad_part = check_archive.testzip()
                if bad_part:
                    raise ValueError(f"Oluşturulan Excel dosyası doğrulanamadı: {bad_part}")
        os.replace(temp_path, final_path)
        temp_path = None
        return {
            "message": (
                f"{stats['rows']:,} satır işlendi; {stats['changed']:,} başlık düzenlendi, "
                f"{stats['blank']:,} kaynak başlık boştu, "
                f"{stats['no_identity']:,} satırda yalnızca çıkarılacak ifadeler vardı."
            ),
            "output_path": str(destination_folder),
            "file_path": str(final_path),
            "rows": stats["rows"],
            "stats": stats.copy(),
        }
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
