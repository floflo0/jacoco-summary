"""Utils functions."""

import re

from .color import Color


def percentage_bar(value_missed: int, value_covered: int) -> str:
    """Return the progress bar corresponding to the percentage of number of
    covered items over total items.

    Args:
        value_missed: the number of items missed
        value_covered: the number of items covered.
    """
    total: int = value_missed + value_covered
    if total == 0:
        return f'{Color.GRAY}━━━━━━━━━━{Color.RESET}  n/a'

    percentage: float = value_covered / total
    result: str = ''
    first_red: bool = True
    for i in range(1, 11):
        if i * 0.1 <= percentage:
            if i == 1:
                result += str(Color.GREEN)
            result += '━'
        elif first_red and i != 1:
            result += f'{Color.RED}╺'
            first_red = False
        else:
            if i == 1:
                result += str(Color.RED)
                first_red = False
            result += '━'
    return result + f'{Color.RESET} {percentage * 100:3.0f}%'


def get_string_width(string: str) -> int:
    """Compute the displayed length of a string in charaters and ignore the
    invisible charaters."""
    return len(re.sub(r'\x1b\[[0-9]*m', '', string))
