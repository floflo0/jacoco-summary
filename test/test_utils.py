"""Test the utils module."""

from unittest import TestCase

from jacoco_summary.utils import get_string_width, percentage_bar


class TestPercentageBar(TestCase):
    """Test the percentage_bar function."""

    def test_percentage_bar_100(self) -> None:
        """Test percentage_bar with 100%."""
        self.assertEqual(
            percentage_bar(0, 5),
            '\x1b[32m━━━━━━━━━━\x1b[0m 100%'
        )

    def test_percentage_bar_0(self) -> None:
        """Test percentage_bar with 0%."""
        self.assertEqual(
            percentage_bar(5, 0),
            '\x1b[31m━━━━━━━━━━\x1b[0m   0%'
        )

    def test_percentage_bar_50(self) -> None:
        """Test percentage_bar with 50%."""
        self.assertEqual(
            percentage_bar(5, 5),
            '\x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50%'
        )

    def test_percentage_bar_33(self) -> None:
        """Test percentage_bar with 50%."""
        self.assertEqual(
            percentage_bar(10, 5),
            '\x1b[32m━━━\x1b[31m╺━━━━━━\x1b[0m  33%'
        )

    def test_percentage_bar_na(self) -> None:
        """Test percentage_bar with n/a percentage."""
        self.assertEqual(
            percentage_bar(0, 0),
            '\x1b[30m━━━━━━━━━━\x1b[0m  n/a'
        )


class TestGetStringWidth(TestCase):
    """Test the get_string_width function."""

    def test_get_string_width(self) -> None:
        """Test get_string_width with a classic string."""
        self.assertEqual(get_string_width('Hello, World!'), 13)

    def test_get_string_width_with_invisible_character(self) -> None:
        """Test get_string_width with a string with invisible characters."""
        self.assertEqual(
            get_string_width('\x1b[32mHello, \x1b[33mWorld!\x1b[0m'),
            13
        )
