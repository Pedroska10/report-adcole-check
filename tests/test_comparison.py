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
    def test_template_500_angle_error_to_uz_only_lobe_six_is_missing(self):
        base_rows = [
            measurement(f"Angle error to UZ - Lobe {lobe}", 306.0 + lobe)
            for lobe in range(1, 7)
        ]
        secondary_rows = {
            f"angleerrortouz-lobe{lobe}": measurement(
                f"Angle error to UZ - Lobe {lobe}", 306.0 + lobe
            )
            for lobe in range(1, 6)
        }

        from comparator_app.mapping import get_mapping_rules_for_selection

        compared = compare_rows(
            base_rows,
            secondary_rows,
            get_mapping_rules_for_selection("3070996", ["Adcole 911"]),
        )

        self.assertEqual([row.status for row in compared], ["ok"] * 5 + ["not ok"])
        self.assertTrue(compared[5].secondary_missing)

    def test_correlated_name_identifies_both_reports(self):
        compared = compare_rows(
            [measurement("Cylindricity - A", 0.008)],
            {"cylindricity-a": measurement("Cylindricitet - Lager A", 0.008)},
            [],
        )

        self.assertEqual(compared[0].status, "ok")
        self.assertEqual(
            compared[0].secondary_name,
            "Cylindricitet - Lager A (Adcole) / Cylindricity - A (Piweb)",
        )

    def test_template_500_maps_cam_11_a6_and_uz_lobes_one_to_five(self):
        names = [
            *(f"Angle error to Cam 11 A6 - Lobe {lobe}" for lobe in range(1, 6)),
            *(f"Angle error to UZ - Lobe {lobe}" for lobe in range(1, 6)),
            "Angle error to Cam 11 A6 - Lobe 6",
            "Angle error to UZ - Lobe 6",
        ]
        base_rows = [measurement(name, 1.0) for name in names]
        secondary_rows = {
            "angleerrortocam11a6-lobe1": measurement(names[0], 1.0),
            "angleerrortocam11a6-lobe2": measurement(names[1], 1.0),
            "angleerrortocam11a6-lobe3": measurement(names[2], 1.0),
            "angleerrortocam11a6-lobe4": measurement(names[3], 1.0),
            "angleerrortocam11a6-lobe5": measurement(names[4], 1.0),
            **{
                f"angleerrortouz-lobe{lobe}": measurement(
                    f"Angle error to UZ - Lobe {lobe}", 1.0
                )
                for lobe in range(1, 6)
            },
        }

        from comparator_app.mapping import get_mapping_rules_for_selection

        compared = compare_rows(
            base_rows,
            secondary_rows,
            get_mapping_rules_for_selection("3070996", ["Adcole 911"]),
        )

        self.assertEqual([row.status for row in compared], ["ok"] * 10 + ["not ok"] * 2)
        self.assertTrue(compared[10].secondary_missing)
        self.assertTrue(compared[11].secondary_missing)

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