from django.test import TestCase
from main.constants import checkout_map
import re


class ConstantsTests(TestCase):

    def test_checkout_map_values(self):
        """Test that checkout suggestions are valid"""
        # Regex to match S/D/T followed by a number
        regex = r"([SDT])(\d+)"

        for key, list_of_checkouts in checkout_map.items():
            for value in list_of_checkouts:
                values = value.split(" ")
                self.assertIn(values[-1][0], ["D", "B"], f"last dart value must be a double")
                round_value = 0
                for dart_value in values:
                    if dart_value == "BULL":
                        dart_value = "D25"
                    match = re.match(regex, dart_value)
                    if match:
                        multiplier_type = match.group(1)
                        multiplier_value = int(match.group(2))

                        match multiplier_type:
                            case "S":
                                multiplier_value = multiplier_value * 1
                            case "D":
                                multiplier_value = multiplier_value * 2
                            case "T":
                                multiplier_value = multiplier_value * 3
                        round_value += multiplier_value
                self.assertEqual(
                    round_value, key, f"Failed for key {key} with value {value}"
                )
