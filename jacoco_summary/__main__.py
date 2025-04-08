#!/usr/bin/python

import sys

from .cli import cli


def main() -> None:
    sys.exit(cli(sys.argv))


main()
