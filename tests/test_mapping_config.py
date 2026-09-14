import re
import unittest

from comparator_app.mapping import (
    MACHINE_OPTIONS,
    get_mapping_rules_for_selection,
    get_mapping_text_for_selection,
    get_part_codes_for_machine,
)


class MappingSelectionTests(unittest.TestCase):
    def test_machine_options_are_available(self):
        self.assertTrue(MACHINE_OPTIONS)
        self.assertIn("Adcole 911", MACHINE_OPTIONS)
        self.assertIn("Adcole LX", MACHINE_OPTIONS)
        self.assertIn("Adcole 1200DH", MACHINE_OPTIONS)

    def test_get_mapping_text_for_selection_uses_part_preset(self):
        text = get_mapping_text_for_selection("EC-001", ["Adcole 911"])
        self.assertIn("^diametromancal", text)
        self.assertIn("^angleerrortocam1-lobe", text)

    def test_template_68_is_selected_for_its_part_codes(self):
        template_68_text = get_mapping_text_for_selection("1865230", ["Adcole 911"])
        reused_template_text = get_mapping_text_for_selection("2208002", ["Adcole 911"])

        self.assertEqual(template_68_text, reused_template_text)
        self.assertIn("^angleerrortocam1-lobe", template_68_text)

    def test_template_63_is_selected_for_its_part_codes(self):
        template_63_text = get_mapping_text_for_selection("2181766", ["Adcole 911"])
        reused_template_text = get_mapping_text_for_selection("1832910", ["Adcole 911"])

        self.assertEqual(template_63_text, reused_template_text)
        self.assertIn("^angleerrortocam1-lobe", template_63_text)
        self.assertIn("diametromancal([a-f])", template_63_text)
        self.assertIn("((?:[1-9]|10))", template_63_text)

        rules = get_mapping_rules_for_selection("2181766", ["Adcole 911"])
        angle_rule = next(pattern for pattern, _ in rules if "angleerrortocam1" in pattern.pattern)
        self.assertEqual(angle_rule.sub("angleerrorcam1-lobe\\1", "angleerrortocam1-lobe2"), "angleerrorcam1-lobe2")

    def test_template_500_is_selected_for_3070996(self):
        template_500_text = get_mapping_text_for_selection("3070996", ["Adcole 911"])

        self.assertIn("^angleerrorcam11a6-lobe", template_500_text)
        self.assertIn("^diametro", template_500_text)
        self.assertNotEqual(
            template_500_text,
            get_mapping_text_for_selection("2181766", ["Adcole 911"]),
        )

        for part_code in ("3073595", "3073597"):
            self.assertEqual(
                template_500_text,
                get_mapping_text_for_selection(part_code, ["Adcole 911"]),
            )

    def test_get_part_codes_for_machine_returns_catalog(self):
        codes = get_part_codes_for_machine("Adcole 911")
        self.assertTrue(codes)
        self.assertIn("150991", codes)
        self.assertIn("2960401", codes)
        self.assertIn("3148774", codes)

    def test_get_mapping_rules_for_selection_returns_valid_rules(self):
        rules = get_mapping_rules_for_selection("EC-001", ["Adcole 911"])
        self.assertTrue(rules)
        for pattern, replacement in rules:
            self.assertIsInstance(pattern, re.Pattern)
            self.assertIsInstance(replacement, str)


if __name__ == "__main__":
    unittest.main()
