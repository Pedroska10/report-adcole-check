import unittest

from comparator_app.parsers import _parse_secondary_pdf_portuguese, _parse_secondary_pdf_template_500
from comparator_app.utils import normalize_key


class Template500ParserTests(unittest.TestCase):
    def test_portuguese_fallback_does_not_create_generic_swedish_rows(self):
        data = _parse_secondary_pdf_portuguese([
            "Cylindricitet",
            "Lager A ,000 ,000 ,020 ,008 ,008",
        ])

        self.assertNotIn("lagera", data)

    def test_parses_swedish_sections_and_f_g_journal_aliases(self):
        lines = [
            "Diameter (undre)",
            "Lager A 35,967 -,008 ,008 35,966 -,001",
            "Diameter (mitten)",
            "Lager F nedre 47,967 -,008 ,008 47,965 -,002",
            "Lager F övre 47,967 -,008 ,008 47,965 -,002",
            "GC radie",
            "A1 25,000 -,100 ,100 25,057 ,057",
            "Vinkelfel kam till indexkam (procesmått)",
            "A1 ,000 -,125 ,125 ,000 ,000",
            "Profilfel Topp",
            "A1 ,000 -,100 ,100 ,041 ,041",
            "Vinkel mellan ytorna U-Z 40,000 -,007 ,007 40,002 ,002",
            "Avstånd område U till ref.axel 39,700 -,050 ,050 39,689 -,011",
            "Vinkelfel kam till ref. U-Z",
            "A1 306,200 -,100 ,100 306,177 -,023",
            "A2 236,100 -,100 ,100 236,081 -,019",
            "A3 22,500 -,100 ,100 22,481 -,019",
            "A4 168,900 -,100 ,100 168,870 -,030",
            "A5 98,800 -,100 ,100 98,777 -,023",
            "(Konkav-Konvex)",
            "A1 ,000 -,005 ,005 ,001 ,001",
            "A2 ,000 -,005 ,005 ,001 ,001",
            "A3 ,000 -,005 ,005 ,001 ,001",
            "A4 ,000 -,005 ,005 ,001 ,001",
            "A5 ,000 -,005 ,005 ,001 ,001",
            "Profilfel Stäng",
            "A1 ,000 -,050 ,050 ,039 ,039",
            "A2 ,000 -,050 ,050 ,030 ,030",
            "A3 ,000 -,050 ,050 ,030 ,030",
            "A4 ,000 -,050 ,050 ,031 ,031",
            "A5 ,000 -,050 ,050 ,032 ,032",
            "Språngavvikelse",
            "A1 ,000 ,000 ,010 ,003 ,003",
            "A2 ,000 ,000 ,010 ,003 ,003",
        ]

        data = _parse_secondary_pdf_template_500(lines)

        self.assertEqual(data[normalize_key("Diametro A [Inf]")].measured_value, 35.966)
        self.assertEqual(data[normalize_key("Diametro F [Center]")].measured_value, 47.965)
        self.assertEqual(data[normalize_key("Diametro G [Center]")].measured_value, 47.965)
        self.assertEqual(data["bcradiuserror-lobe1"].measured_value, 25.057)
        self.assertEqual(data["angleerrortocam11a6-lobe1"].measured_value, 0.0)
        self.assertEqual(data["lifterrornose-lobe1"].measured_value, 0.041)
        self.assertEqual(data["anguloentreassuperficies"].measured_value, 40.002)
        self.assertEqual(data["distanciauparaoeixoderot"].measured_value, 39.689)
        self.assertEqual(data["angleerrortouz-lobe1"].measured_value, 306.177)
        self.assertEqual(data["angleerrortouz-lobe5"].measured_value, 98.777)
        self.assertEqual(data["concaveconvex-lobe1"].measured_value, 0.001)
        self.assertEqual(data["concaveconvex-lobe5"].measured_value, 0.001)
        self.assertEqual(data["lifterrorclosingramp-lobe1"].measured_value, 0.039)
        self.assertEqual(data["lifterrorclosingramp-lobe5"].measured_value, 0.032)
        self.assertEqual(data["sprangavvikelse-lobe1"].measured_value, 0.003)


if __name__ == "__main__":
    unittest.main()