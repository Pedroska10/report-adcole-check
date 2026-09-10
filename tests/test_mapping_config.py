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
