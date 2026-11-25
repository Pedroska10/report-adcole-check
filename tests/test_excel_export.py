import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Border, Side

from comparator_app.excel_export import write_output_excel
from comparator_app.models import ComparedRow, MeasurementRow


class ExcelExportLayoutTests(unittest.TestCase):
    def test_export_removes_unused_borders_and_wraps_long_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.xlsx"
            output_path = Path(temp_dir) / "output.xlsx"

            workbook = Workbook()
            sheet = workbook.active
            sheet.merge_cells("B1:C1")
            sheet["B1"] = "CHARACTERISTIC"
            sheet["B2"] = "adcole"
            sheet["C2"] = "piweb"
            border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )
            for row in range(1, 16):
                for column in range(1, 11):
                    sheet.cell(row, column).border = border
            workbook.save(model_path)

            measurement = MeasurementRow(
                characteristic_name="",
                nominal_value=0.0,
                measured_value=0.1,
                lower_limit=-0.2,
                upper_limit=0.2,
                deviation=0.1,
                exceedance=0.0,
            )
            compared_row = ComparedRow(
                row=measurement,
                secondary_name=None,
                status="ok",
                mismatched_fields=set(),
                secondary_missing=False,
                adcole_name="A long Adcole characteristic name that needs wrapping",
                piweb_name="A long Piweb characteristic name that needs wrapping",
            )

            second_row = ComparedRow(
                row=measurement,
                secondary_name=None,
                status="not ok",
                mismatched_fields={"measured_value"},
                secondary_missing=False,
                adcole_name="Second characteristic",
                piweb_name="Second characteristic",
            )
            write_output_excel([compared_row, second_row], model_path, output_path)

            result = load_workbook(output_path)
            output = result.active
            self.assertEqual(output.max_row, 4)
            self.assertIsNone(output["B5"].border.bottom.style)
            self.assertEqual(output["B3"].border.bottom.style, "thin")
            self.assertTrue(output["B3"].alignment.wrap_text)
            self.assertGreaterEqual(output.row_dimensions[3].height, 30)
            self.assertLessEqual(output.column_dimensions["B"].width, 52)
            self.assertGreaterEqual(output.row_dimensions[2].height, 34)
            self.assertEqual(output["E2"].value, "Measured Value")
            self.assertEqual(output.tables["ReportComparison"].ref, "A2:J4")
            self.assertGreaterEqual(output.column_dimensions["A"].width, 16)
            self.assertEqual(output["D1"].font.color.rgb[-6:], "FFFFFF")
            self.assertEqual(output["J1"].font.color.rgb[-6:], "FFFFFF")
            self.assertIsNone(output["A3"].fill.fill_type)
            self.assertIsNone(output["A4"].fill.fill_type)
            self.assertEqual(output["E4"].fill.fgColor.rgb[-6:], "F4CCCC")
            self.assertEqual(output["J4"].fill.fgColor.rgb[-6:], "F4CCCC")


if __name__ == "__main__":
    unittest.main()
