from pathlib import Path
from copy import copy

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Alignment, Font
from openpyxl.styles import PatternFill

from .models import ComparedRow


LIGHT_RED_FILL = PatternFill(fill_type="solid", fgColor="FFF4CCCC")


def _set_cell_value(sheet, row: int, column: int, value) -> None:
    cell = sheet.cell(row=row, column=column)
    if not isinstance(cell, MergedCell):
        cell.value = value


def _clear_cell(sheet, row: int, column: int) -> None:
    cell = sheet.cell(row=row, column=column)
    if not isinstance(cell, MergedCell):
        cell.value = None
        cell.fill = PatternFill(fill_type=None)


def write_output_excel(
    compared_rows: list[ComparedRow],
    model_path: Path,
    output_path: Path,
) -> None:
    workbook = load_workbook(str(model_path))
    sheet = workbook[workbook.sheetnames[0]]
    has_characteristic_group = (
        sheet.cell(1, 2).value == "CHARACTERISTIC"
        and sheet.cell(2, 2).value == "adcole"
        and sheet.cell(2, 3).value == "piweb"
    )
    if not has_characteristic_group:
        sheet.insert_cols(3, 1)

    if "B1:C1" not in {str(merged_range) for merged_range in sheet.merged_cells.ranges}:
        sheet.merge_cells("B1:C1")
    _set_cell_value(sheet, 1, 2, "CHARACTERISTIC")
    _set_cell_value(sheet, 2, 2, "adcole")
    _set_cell_value(sheet, 2, 3, "piweb")
    for cell in (sheet.cell(1, 2), sheet.cell(2, 2), sheet.cell(2, 3)):
        if isinstance(cell, MergedCell):
            continue
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(bold=True)

    characteristic_header = sheet.cell(1, 2)
    if not isinstance(characteristic_header, MergedCell):
        characteristic_font = copy(characteristic_header.font)
        characteristic_font.color = "FFFFFF"
        characteristic_header.font = characteristic_font

    _set_cell_value(sheet, 1, 1, "Column1")
    _set_cell_value(sheet, 2, 1, None)
    for column in range(4, 11):
        _set_cell_value(sheet, 2, column, None)
    for column, value in enumerate(
        ["NOMINAL VALUE", "MEASURED VALUE", "LOWER LIMIT", "UPPER LIMIT", "DEVIATION", "EXCEEDANCE", "NOT OK"],
        start=4,
    ):
        _set_cell_value(sheet, 1, column, value)

    max_row = sheet.max_row
    for row_index in range(3, max_row + 1):
        for col in range(1, 11):
            _clear_cell(sheet, row_index, col)

    field_to_excel_col = {
        "nominal_value": 3,
        "measured_value": 4,
        "lower_limit": 5,
        "upper_limit": 6,
        "deviation": 7,
        "exceedance": 8,
    }

    for i, compared in enumerate(compared_rows, start=3):
        if i > sheet.max_row:
            sheet.append([None] * 10)

        row = compared.row
        _set_cell_value(sheet, i, 1, i - 2)
        _set_cell_value(sheet, i, 2, compared.adcole_name)
        _set_cell_value(sheet, i, 3, compared.piweb_name or (
            None if compared.base_missing else row.characteristic_name
        ))
        _set_cell_value(sheet, i, 4, row.nominal_value)
        _set_cell_value(sheet, i, 5, row.measured_value)
        _set_cell_value(sheet, i, 6, row.lower_limit)
        _set_cell_value(sheet, i, 7, row.upper_limit)
        _set_cell_value(sheet, i, 8, row.deviation)
        _set_cell_value(sheet, i, 9, row.exceedance)
        _set_cell_value(sheet, i, 10, compared.status)

        for field_name in compared.mismatched_fields:
            excel_col = field_to_excel_col[field_name] + 1
            cell = sheet.cell(i, excel_col)
            if not isinstance(cell, MergedCell):
                cell.fill = LIGHT_RED_FILL

        if compared.status == "not ok":
            cell = sheet.cell(i, 10)
            if not isinstance(cell, MergedCell):
                cell.fill = LIGHT_RED_FILL

    workbook.save(str(output_path))
