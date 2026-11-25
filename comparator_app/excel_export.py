from pathlib import Path
from copy import copy
from math import ceil

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Alignment, Font
from openpyxl.styles import PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

from .models import ComparedRow


LIGHT_RED_FILL = PatternFill(fill_type="solid", fgColor="FFF4CCCC")
MIN_TEXT_COLUMN_WIDTH = 24
MAX_TEXT_COLUMN_WIDTH = 52
MAX_VALUE_COLUMN_WIDTH = 18


def _set_cell_value(sheet, row: int, column: int, value) -> None:
    cell = sheet.cell(row=row, column=column)
    if not isinstance(cell, MergedCell):
        cell.value = value


def _clear_cell(sheet, row: int, column: int) -> None:
    cell = sheet.cell(row=row, column=column)
    if not isinstance(cell, MergedCell):
        cell.value = None
        cell.fill = PatternFill(fill_type=None)


def _fit_output_cells(sheet, last_row: int, last_column: int) -> None:
    for column in range(1, last_column + 1):
        max_length = max(
            (
                len(str(sheet.cell(row, column).value))
                for row in range(1, last_row + 1)
                if sheet.cell(row, column).value is not None
            ),
            default=0,
        )
        if column in {2, 3}:
            width = min(
                max(MIN_TEXT_COLUMN_WIDTH, max_length + 2),
                MAX_TEXT_COLUMN_WIDTH,
            )
        else:
            width = min(max(8, max_length + 2), MAX_VALUE_COLUMN_WIDTH)
        if column == 1:
            width = max(width, 16)
        sheet.column_dimensions[get_column_letter(column)].width = width

    text_column_widths = {
        column: int(sheet.column_dimensions[get_column_letter(column)].width)
        for column in (2, 3)
    }
    for row_index in range(1, last_row + 1):
        line_count = 1
        for column in range(1, last_column + 1):
            cell = sheet.cell(row_index, column)
            if isinstance(cell, MergedCell):
                continue
            alignment = copy(cell.alignment)
            alignment.wrap_text = True
            alignment.vertical = "center"
            cell.alignment = alignment
            if cell.value is None:
                continue
            text = str(cell.value)
            width = (
                text_column_widths[column]
                if column in text_column_widths
                else int(sheet.column_dimensions[get_column_letter(column)].width)
            )
            wrapped_lines = sum(max(1, ceil(len(line) / width)) for line in text.splitlines())
            line_count = max(line_count, wrapped_lines)
        minimum_height = 28 if row_index == 1 else 34 if row_index == 2 else 18
        sheet.row_dimensions[row_index].height = max(minimum_height, line_count * 15)


def write_output_excel(
    compared_rows: list[ComparedRow],
    model_path: Path,
    output_path: Path,
) -> None:
    workbook = load_workbook(str(model_path))
    sheet = workbook[workbook.sheetnames[0]]
    has_characteristic_group = (
        sheet.cell(1, 2).value == "CHARACTERISTIC"
        and str(sheet.cell(2, 2).value).lower() == "adcole"
        and str(sheet.cell(2, 3).value).lower() == "piweb"
    )
    if not has_characteristic_group:
        sheet.insert_cols(3, 1)

    merged_ranges = {str(merged_range) for merged_range in sheet.merged_cells.ranges}
    if "D1:I1" in merged_ranges:
        sheet.unmerge_cells("D1:I1")
    if "B1:C1" not in merged_ranges:
        sheet.merge_cells("B1:C1")
    _set_cell_value(sheet, 1, 2, "CHARACTERISTIC")
    sheet.merge_cells("D1:I1")
    _set_cell_value(sheet, 1, 4, "MEASUREMENTS")
    _set_cell_value(sheet, 1, 10, "RESULT")
    for cell in (sheet.cell(1, 2), sheet.cell(1, 4), sheet.cell(1, 10)):
        if isinstance(cell, MergedCell):
            continue
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(bold=True)

    characteristic_header = sheet.cell(1, 2)
    if not isinstance(characteristic_header, MergedCell):
        characteristic_font = copy(characteristic_header.font)
        characteristic_font.color = "FFFFFF"
        characteristic_header.font = characteristic_font
    for cell in (sheet.cell(1, 4), sheet.cell(1, 10)):
        if not isinstance(cell, MergedCell):
            group_font = copy(cell.font)
            group_font.color = "FFFFFF"
            group_font.bold = True
            cell.font = group_font

    _set_cell_value(sheet, 1, 1, "COMPARISON")
    table_headers = [
        "No.",
        "Adcole",
        "Piweb",
        "Nominal Value",
        "Measured Value",
        "Lower Limit",
        "Upper Limit",
        "Deviation",
        "Exceedance",
        "Status",
    ]
    for column, value in enumerate(table_headers, start=1):
        _set_cell_value(sheet, 2, column, value)
        cell = sheet.cell(2, column)
        if not isinstance(cell, MergedCell):
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.font = Font(bold=True)

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
        _set_cell_value(sheet, i, 2, compared.adcole_name or "Nao encontrada")
        _set_cell_value(sheet, i, 3, compared.piweb_name or "Nao encontrada")
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

    last_content_row = max(2, len(compared_rows) + 2)
    if sheet.max_row > last_content_row:
        sheet.delete_rows(last_content_row + 1, sheet.max_row - last_content_row)
    _fit_output_cells(sheet, last_content_row, 10)

    for table_name in list(sheet.tables):
        del sheet.tables[table_name]
    existing_names = {
        table.displayName.lower()
        for worksheet in workbook.worksheets
        for table in worksheet.tables.values()
    }
    table_name = "ReportComparison"
    suffix = 2
    while table_name.lower() in existing_names:
        table_name = f"ReportComparison{suffix}"
        suffix += 1
    table = Table(displayName=table_name, ref=f"A2:J{last_content_row}")
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=False,
        showColumnStripes=False,
    )
    sheet.add_table(table)

    workbook.save(str(output_path))
