
import unittest
from unittest.mock import patch

from main import (
    ClothingItem,
    colours_match,
    generate_outfit,
    score_outfit,
)


class TestStyleMe(unittest.TestCase):

    def test_matching_colours(self):
        self.assertTrue(colours_match("Black", "White"))

    def test_same_colour_matches(self):
        self.assertTrue(colours_match("Pink", "Pink"))

    def test_colour_matching_ignores_case(self):
        self.assertTrue(colours_match("black", "WHITE"))

    def test_incompatible_colours(self):
        self.assertFalse(colours_match("Green", "Pink"))

    def test_outfit_requires_all_categories(self):
        # An empty wardrobe should not produce an outfit.
        with patch("main.load_wardrobe", return_value=[]):
            outfit = generate_outfit(
                "Feminine",
                "Date",
                "Warm",
            )

        self.assertIsNone(outfit)

    def test_outfit_contains_correct_categories(self):
        wardrobe = [
            ClothingItem("Pink fitted top", "Top", "Pink", "Feminine"),
            ClothingItem("Black mini skirt", "Bottom", "Black", "Feminine"),
            ClothingItem("Black ballet flats", "Shoes", "Black", "Feminine"),
        ]

        with patch("main.load_wardrobe", return_value=wardrobe):
            outfit = generate_outfit(
                "Feminine",
                "Date",
                "Warm",
            )

        self.assertIsNotNone(outfit)

        top, bottom, shoes = outfit

        self.assertEqual(top.category, "Top")
        self.assertEqual(bottom.category, "Bottom")
        self.assertEqual(shoes.category, "Shoes")

    def test_outfit_scoring_returns_a_number(self):
        top = ClothingItem("Pink fitted top", "Top", "Pink", "Feminine")
        bottom = ClothingItem("Black mini skirt", "Bottom", "Black", "Feminine")
        shoes = ClothingItem("Black ballet flats", "Shoes", "Black", "Feminine")

        score = score_outfit(
            top,
            bottom,
            shoes,
            "Feminine",
            "Date",
            "Warm",
        )

        self.assertIsInstance(score, (int, float))


if __name__ == "__main__":
    unittest.main()