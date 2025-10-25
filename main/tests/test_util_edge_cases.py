from django.test import TestCase
from main.business_logic.utils import get_points_of_round
from main.constants import checkout_map, IMPOSSIBLE_POINTS


class SingleplayerGameTests(TestCase):

    def test_all_throws(self):
        for i in range(1, 181):
            estimated_points = i if i not in IMPOSSIBLE_POINTS else 0
            self.assertEqual(get_points_of_round(501, i), estimated_points)

    def test_all_checkouts(self):
        for i in range(1, 181):
            estimated_points = i if i in checkout_map else 0
            self.assertEqual(get_points_of_round(i, i), estimated_points)
