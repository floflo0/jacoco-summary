import argparse
import os
import sys
from typing import NoReturn
from xml.etree.ElementTree import ParseError

from . import __version__
from .config import COLUMNS_ORDER, JACOCO_XML_FILE_PATH
from .report import Report
from .source_file_coverage import SourceFileCoverage
from .table import generate_table, print_table
from .xml_parsing_exception import XmlParsingException


EXIT_SUCCESS: int = 0
EXIT_FAILURE: int = 1


def print_packages(jacoco_report: Report) -> None:
    for package_name in sorted(jacoco_report.get_packages_names()):
        print(package_name)


def print_files(jacoco_report: Report) -> None:
    for file_name in sorted(jacoco_report.get_source_files_names()):
        print(file_name)


class ArgumentParser(argparse.ArgumentParser):
    '''Custom ArgumentParser that change exit code to 1 on error.'''

    def exit(self, status: int = EXIT_SUCCESS, message: str | None = None
             ) -> NoReturn:
        if message:
            self._print_message(message, sys.stderr)
        if status != EXIT_SUCCESS:
            status = EXIT_FAILURE
        sys.exit(status)


def cli(args: list[str]) -> int:
    assert args, 'args is empty'

    program_name = os.path.basename(args[0])

    def print_error(*message: str) -> None:
        """Print a formated error message in stderr.

        Args:
            message: the message to print
        """
        print(f'{program_name}: error:', *message, file=sys.stderr)

    global_parser = ArgumentParser(prog=program_name, add_help=False)
    global_parser.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        default=JACOCO_XML_FILE_PATH,
        help='the path JaCoCo report xml file to use'
    )

    main_parser = ArgumentParser(
        prog=program_name,
        description='Display JaCoCo test coverage result in a fancy way.',
        parents=[global_parser]
    )
    main_parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    subparsers = main_parser.add_subparsers(
        title='subcommands',
        dest='subcommand'
    )
    package_parser = subparsers.add_parser(
        'package',
        help='print the summary of a specific package',
        description='Print the summary of a specific package.',
        parents=[global_parser]
    )
    package_metavar: str = 'PACKAGE'
    package_parser.add_argument(
        'package',
        metavar=package_metavar,
        nargs='?',
        help='the name of the package to display'
    )
    package_parser.add_argument(
        '-l',
        '--list-packages',
        action='store_true',
        help='list packages in the report'
    )
    class_parser = subparsers.add_parser(
        'class',
        help='print the summary of a specific class',
        description='Print the summary of a specific class.',
        parents=[global_parser]
    )
    class_parser.add_argument(
        'java_class',
        metavar='CLASS',
        help='the name of the class to display'
    )

    file_metavar: str = 'JAVA_FILE'
    file_parser  = subparsers.add_parser(
        'file',
        help='print the summary per files',
        description='Print the summary per files.',
        parents=[global_parser]
    )
    file_parser.add_argument(
        'java_file',
        metavar=file_metavar,
        nargs='?',
        help='the path to a file in the report to display'
    )
    file_parser.add_argument(
        '-l',
        '--list-files',
        action='store_true',
        help='list files in the report'
    )

    # Display the right usage message when there is an error in parsing args.
    global_parser.print_usage = main_parser.print_usage  # type: ignore

    global_args, remaining_args = global_parser.parse_known_args(args[1:])
    parsed_args: argparse.Namespace = main_parser.parse_args(remaining_args)
    file: str = global_args.file
    subcommand: str | None = parsed_args.subcommand

    try:
        project_coverage = Report.from_xml_file(file)
    except FileNotFoundError:
        print_error(f'{file}: no such file or directory')
        return EXIT_FAILURE
    except ParseError as error:
        print_error(f'{file}: failed to parse file: {error}')
        return EXIT_FAILURE
    except XmlParsingException as exception:
        print_error(f'{file}: {exception}')
        return EXIT_FAILURE

    if subcommand == 'package':
        list_packages: bool = parsed_args.list_packages
        if list_packages:
            print_packages(project_coverage)
            return EXIT_SUCCESS
        package_name: str | None = parsed_args.package
        if package_name is None:
            package_parser.error(
                f'the following arguments are required: {package_metavar}'
            )
        package = project_coverage.get_package(package_name)
        if package is None:
            print_error(f'package {repr(package_name)} doesn\'t exists')
            return EXIT_FAILURE
        if len(package.classes) == 0:
            print('There is no class in this package.')
            return EXIT_SUCCESS
        print_table(generate_table(package.classes, COLUMNS_ORDER))
        return EXIT_SUCCESS

    if subcommand == 'class':
        java_class_name: str = parsed_args.java_class
        java_class = project_coverage.get_class(java_class_name)
        if java_class is None:
            print_error(f'class {repr(java_class_name)} doesn\'t exists')
            return EXIT_FAILURE
        if len(java_class.methods) == 0:
            print('No methods found in this class.')
            return EXIT_SUCCESS
        print_table(generate_table(java_class.methods, COLUMNS_ORDER))
        return EXIT_SUCCESS

    if subcommand == 'file':
        list_files: bool = parsed_args.list_files
        if list_files:
            print_files(project_coverage)
            return EXIT_SUCCESS

        java_file_name: str | None = parsed_args.java_file
        source_files: list[SourceFileCoverage]
        if java_file_name is not None:
            java_file = project_coverage.get_source_file(java_file_name)
            if java_file is None:
                print_error(f'file {repr(java_file_name)} doesn\'t exists')
                return EXIT_FAILURE
            source_files = [java_file]
        else:
            source_files = project_coverage.get_source_files()
        print_table(generate_table(source_files, COLUMNS_ORDER))
        return EXIT_SUCCESS

    classes = project_coverage.get_classes()
    if not classes:
        print('No classes found.')
        return EXIT_SUCCESS
    tab = generate_table(project_coverage.get_classes(), COLUMNS_ORDER)
    print_table(tab)
    return EXIT_SUCCESS
