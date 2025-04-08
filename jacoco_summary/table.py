from collections.abc import Sequence

from .column_name import ColumnName
from .coverage import Coverage
from .utils import get_string_width


def generate_table(lines: Sequence[Coverage], columns_order: list[ColumnName]
                 ) -> list[list[str]]:
    tab: list[list[str]] = [[column.value for column in columns_order]]
    for coverage in lines:
        tab.append([coverage.get_field(column) for column in columns_order])
    return tab


def print_table_cell(cell_content: str, max_size: int) -> None:
    print(
        f'│ {cell_content}',
        ' ' * (max_size - get_string_width(cell_content)),
        end=''
    )


def print_table_end_line() -> None:
    print('│')


def print_table_header(tab_header: list[str], columns_max_size: list[int]
                     ) -> None:
    print('┌', end='')
    for i, column in enumerate(tab_header):
        print('─' * (columns_max_size[i] + 2), end='')
        if i != len(tab_header) - 1:
            print('┬', end='')
    print('┐')
    for i, column in enumerate(tab_header):
        print_table_cell(column, columns_max_size[i])
    print_table_end_line()
    print('├', end='')
    for i, column in enumerate(tab_header):
        print('─' * (columns_max_size[i] + 2), end='')
        if i != len(tab_header) - 1:
            print('┼', end='')
    print('┤')


def print_table_body(tab_body: list[list[str]], columns_max_size: list[int]
                   ) -> None:
    for line in tab_body:
        for i, column in enumerate(line):
            print_table_cell(column, columns_max_size[i])
        print_table_end_line()


def print_table_footer(columns_size: list[int]) -> None:
    print('└', end='')
    for i, column in enumerate(columns_size):
        print('─' * (column + 2), end='')
        if i != len(columns_size) - 1:
            print('┴', end='')
    print('┘')


def print_table(tab: list[list[str]]) -> None:
    assert tab, 'try to print an empty table'

    columns_max_size: list[int] = [
        max(map(
            get_string_width,
            (line[j] for line in tab)
        )) for j in range(len(tab[0]))
    ]

    print_table_header(tab.pop(0), columns_max_size)
    print_table_body(tab, columns_max_size)
    print_table_footer(columns_max_size)
