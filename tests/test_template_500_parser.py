import unittest

from comparator_app.parsers import _parse_secondary_pdf_template_500
from comparator_app.utils import normalize_key


class Template500ParserTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()