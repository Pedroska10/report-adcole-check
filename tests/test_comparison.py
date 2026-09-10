import unittest

from comparator_app.comparison import compare_rows
from comparator_app.models import MeasurementRow


def measurement(name: str, measured: float) -> MeasurementRow:
    return MeasurementRow(
        characteristic_name=name,
        nominal_value=0.0,
        measured_value=measured,
        lower_limit=0.0,
        upper_limit=1.0,
        deviation=measured,
        exceedance=0.0,
    )


class BidirectionalComparisonTests(unittest.TestCase):
    def test_reports_features_missing_on_either_side(self):
        base_rows = [measurement("Caracteristica do PDF", 0.5)]
        secondary_rows = {
            "caracteristicadopdf": measurement("Caracteristica do PDF", 0.5),
            "somenteamaquina": measurement("Somente a maquina", 0.4),
        }

        compared = compare_rows(base_rows, secondary_rows, [])

        self.assertEqual(len(compared), 2)
        self.assertEqual(compared[0].status, "ok")
        self.assertTrue(compared[1].base_missing)
        self.assertEqual(compared[1].row.characteristic_name, "Somente a maquina")

    def test_reports_pdf_feature_missing_on_machine(self):
        base_rows = [measurement("Somente no PDF", 0.5)]

        compared = compare_rows(base_rows, {}, [])

        self.assertEqual(len(compared), 1)
        self.assertTrue(compared[0].secondary_missing)
        self.assertFalse(compared[0].base_missing)


if __name__ == "__main__":
    unittest.main()