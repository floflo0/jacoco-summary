"""Test the table module."""

from io import StringIO
import sys
from typing import Callable, ParamSpec
from unittest import TestCase

from jacoco_summary.coverage import Coverage
from jacoco_summary.config import COLUMNS_ORDER
from jacoco_summary.table import (
    generate_table,
    print_table_cell,
    print_table_end_line,
    print_table_header,
    print_table_body,
    print_table_footer,
    print_table
)


P = ParamSpec('P')


class TestTable(TestCase):

    maxDiff = 10_000

    def assert_print(self, stdout: str, func: Callable[P, None], *args: P.args,
                     **kwargs: P.kwargs) -> None:
        sys_stdout = sys.stdout
        fake_stdout = StringIO()
        sys.stdout = fake_stdout

        func(*args, **kwargs)

        sys.stdout = sys_stdout

        self.assertEqual(fake_stdout.getvalue(), stdout)

    def test_generate_table(self) -> None:
        """Test generating a table."""
        expected = [
            ['Name', 'Branch', 'Line', 'Method'],
            [
                'Item 1',
                '\x1b[30m━━━━━━━━━━\x1b[0m  n/a',
                '\x1b[30m━━━━━━━━━━\x1b[0m  n/a',
                '\x1b[30m━━━━━━━━━━\x1b[0m  n/a'
            ],
            [
                'Item 2',
                '\x1b[32m━━━━━━━━━━\x1b[0m 100%',
                '\x1b[32m━━━━━━━━━━\x1b[0m 100%',
                '\x1b[32m━━━━━━━━━━\x1b[0m 100%'
            ],
            [
                'Item 3',
                '\x1b[31m━━━━━━━━━━\x1b[0m   0%',
                '\x1b[31m━━━━━━━━━━\x1b[0m   0%',
                '\x1b[31m━━━━━━━━━━\x1b[0m   0%'
            ],
            [
                'Item 4',
                '\x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50%',
                '\x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50%',
                '\x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50%'
            ],
            [
                'Item 5',
                '\x1b[31m━━━━━━━━━━\x1b[0m   0%',
                '\x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50%',
                '\x1b[32m━━━━━━━━━━\x1b[0m 100%'
            ]
        ]
        self.assertEqual(generate_table([
            Coverage('Item 1', 0, 0, 0, 0, 0, 0),
            Coverage('Item 2', 0, 1, 0, 1, 0, 1),
            Coverage('Item 3', 1, 0, 1, 0, 1, 0),
            Coverage('Item 4', 1, 1, 1, 1, 1, 1),
            Coverage('Item 5', 1, 0, 1, 1, 0, 1)
        ], COLUMNS_ORDER), expected)

    def test_generate_table_empty_table(self) -> None:
        """Test generating an empty table."""
        expected = [['Name', 'Branch', 'Line', 'Method']]

        self.assertEqual(generate_table([], COLUMNS_ORDER), expected)

    def test_print_table_cell(self) -> None:
        self.assert_print(
            '│ cell content ',
            print_table_cell,
            'cell content',
            12
        )
        self.assert_print(
            '│ cell content    ',
            print_table_cell,
            'cell content',
            15
        )

    def test_print_table_end_line(self) -> None:
        self.assert_print(
            '│\n',
            print_table_end_line
        )

    def test_print_table_header(self) -> None:
        self.assert_print(
            (
                '┌──────────┬────────────┬──────────────┐\n'
                '│ column 1 │ column 2   │ column 3     │\n'
                '├──────────┼────────────┼──────────────┤\n'
            ),
            print_table_header,
            ['column 1', 'column 2', 'column 3'],
            [8, 10, 12]
        )

    def test_print_table_body(self) -> None:
        self.assert_print(
            (
                '│ cell 1     │ cell 2     │ cell 3     │\n'
                '│ big cell 1 │ big cell 2 │ big cell 3 │\n'
                '│ cell 1     │ c 2        │ big cell 3 │\n'
            ),
            print_table_body,
            [
                ['cell 1', 'cell 2', 'cell 3'],
                ['big cell 1', 'big cell 2', 'big cell 3'],
                ['cell 1', 'c 2', 'big cell 3']
            ],
            [10, 10, 10]
        )

    def test_print_table_footer(self) -> None:
        self.assert_print(
            '└──────────┴────────────┴──────────────┘\n',
            print_table_footer,
            [8, 10, 12]
        )

    def test_print_table(self) -> None:
        self.assert_print(
            (
                '┌────────────┬────────────┬────────────┐\n'
                '│ column 1   │ column 2   │ column 3   │\n'
                '├────────────┼────────────┼────────────┤\n'
                '│ cell 1     │ cell 2     │ cell 3     │\n'
                '│ big cell 1 │ big cell 2 │ big cell 3 │\n'
                '│ cell 1     │ c 2        │ big cell 3 │\n'
                '└────────────┴────────────┴────────────┘\n'
            ),
            print_table,
            [
                ['column 1', 'column 2', 'column 3'],
                ['cell 1', 'cell 2', 'cell 3'],
                ['big cell 1', 'big cell 2', 'big cell 3'],
                ['cell 1', 'c 2', 'big cell 3']
            ],
        )

        empty_table: list[str] = []
        self.assertRaises(AssertionError, print_table, empty_table)
