"""Test the cli module."""

from io import StringIO
import os
import shutil
from typing import Callable
import sys
from unittest import TestCase

from jacoco_summary.cli import cli


class TestCli(TestCase):

    maxDiff = 10_000

    # pylint: disable=line-too-long
    help: str = (
        'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
        '\n'
        'Display JaCoCo test coverage result in a fancy way.\n'
        '\n'
        'options:\n'
        '  -h, --help            show this help message and exit\n'
        '  -f, --file FILE       the path JaCoCo report xml file to use\n'
        "  -v, --version         show program's version number and exit\n"
        '\n'
        'subcommands:\n'
        '  {package,class,file}\n'
        '    package             print the summary of a specific package\n'
        '    class               print the summary of a specific class\n'
        '    file                print the summary per files\n'
    )
    # pylint: enable=line-too-long

    help_package: str = (
        'usage: cli package [-h] [-f FILE] [-l] [PACKAGE]\n'
        '\n'
        'Print the summary of a specific package.\n'
        '\n'
        'positional arguments:\n'
        '  PACKAGE              the name of the package to display\n'
        '\n'
        'options:\n'
        '  -h, --help           show this help message and exit\n'
        '  -f, --file FILE      the path JaCoCo report xml file to use\n'
        '  -l, --list-packages  list packages in the report\n'
    )

    help_class: str = (
        'usage: cli class [-h] [-f FILE] CLASS\n'
        '\n'
        'Print the summary of a specific class.\n'
        '\n'
        'positional arguments:\n'
        '  CLASS            the name of the class to display\n'
        '\n'
        'options:\n'
        '  -h, --help       show this help message and exit\n'
        '  -f, --file FILE  the path JaCoCo report xml file to use\n'
    )

    help_file: str = (
        'usage: cli file [-h] [-f FILE] [-l] [JAVA_FILE]\n'
        '\n'
        'Print the summary per files.\n'
        '\n'
        'positional arguments:\n'
        '  JAVA_FILE         the path to a file in the report to display\n'
        '\n'
        'options:\n'
        '  -h, --help        show this help message and exit\n'
        '  -f, --file FILE   the path JaCoCo report xml file to use\n'
        '  -l, --list-files  list files in the report\n'
    )

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists('target/site/jacoco'):
            shutil.rmtree('target')
        os.makedirs('target/site/jacoco')
        shutil.copyfile('test/jacoco.xml', 'target/site/jacoco/jacoco.xml')

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree('target')

    def assert_command(
        self,
        command: Callable[[list[str]], int],
        args: list[str],
        returncode: int = 0,
        stdout: str = '',
        stderr: str = '',
    ) -> None:
        """Fail if the returncode or the output of the command don't match.

        Args:
            msg: the message print on failure
            command: the command to test
            args: the arguments to pass to the command
            returncode: the expected returncode for the command
            stdout: the expected stdout
            stderr: the expected stderr
        """
        sys_stdout = sys.stdout
        sys_stderr = sys.stderr
        fake_stdout = StringIO()
        fake_stderr = StringIO()
        sys.stdout = fake_stdout
        sys.stderr = fake_stderr

        command_returncode: int
        try:
            command_returncode = command(args)
        except SystemExit as system_exit:
            assert isinstance(system_exit.code, int)
            command_returncode = system_exit.code

        sys.stdout = sys_stdout
        sys.stderr = sys_stderr

        self.assertEqual(command_returncode, returncode, f'{args}: returncode')
        self.assertEqual(fake_stdout.getvalue(), stdout, f'{args}: stdout')
        self.assertEqual(fake_stderr.getvalue(), stderr, f'{args}: stderr')

    def hide_file(self, file: str) -> None:
        os.renames(file, file + '.hide')
        self.addCleanup(lambda: os.renames(file + '.hide', file))

    def test_cli_unknows_option(self) -> None:
        """Test cli with an unknown option."""
        self.assert_command(
            cli,
            ['cli', '--unknown-option'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: unrecognized arguments: --unknown-option\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_doesnt_exists(self) -> None:
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: target/site/jacoco/jacoco.xml: no such file or directory\n'
            # pylint: enable=line-too-long
        )

    def test_cli_help_short_option(self) -> None:
        """Test cli -h option."""
        self.assert_command(
            cli,
            ['cli', '-h'],
            stdout=self.help
        )

    def test_cli_help_long_option(self) -> None:
        """Test cli --help option."""
        self.assert_command(
            cli,
            ['cli', '--help'],
            stdout=self.help
        )

    def test_cli_version_short_option(self) -> None:
        """Test cli -v option."""
        self.assert_command(
            cli,
            ['cli', '-v'],
            stdout='cli 0.0.0\n'
        )

    def test_cli_version_long_option(self) -> None:
        """Test cli --version option."""
        self.assert_command(
            cli,
            ['cli', '--version'],
            stdout='cli 0.0.0\n'
        )

    def test_cli_file_short_option(self) -> None:
        """Test cli -f option."""
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', '-f', 'test/jacoco.xml'],
            stdout=(  # pylint: disable=line-too-long
                '┌──────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name         │ Branch          │ Line            │ Method          │\n'
                '├──────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test2.Class2 │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test2.Class1 │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test1.Class1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1.Class2 │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└──────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_short_option_file_doesnt_exists(self) -> None:
        """Test cli -f option with a file that doesn't exists."""
        self.assert_command(
            cli,
            ['cli', '-f', 'file.xml'],
            returncode=1,
            stderr='cli: error: file.xml: no such file or directory\n'
        )

    def test_cli_file_short_option_file_no_argument(self) -> None:
        """Test cli -f option with no argument."""
        self.assert_command(
            cli,
            ['cli', '-f'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # # pylint: enable=line-too-long
        )

    def test_cli_file_long_option(self) -> None:
        """Test cli --file option."""
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', '--file', 'test/jacoco.xml'],
            stdout=(  # pylint: disable=line-too-long
                '┌──────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name         │ Branch          │ Line            │ Method          │\n'
                '├──────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test2.Class2 │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test2.Class1 │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test1.Class1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1.Class2 │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└──────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_long_option_file_doesnt_exists(self) -> None:
        """Test cli --file option with a file that doesn't exists."""
        self.assert_command(
            cli,
            ['cli', '--file', 'file.xml'],
            returncode=1,
            stderr='cli: error: file.xml: no such file or directory\n'
        )

    def test_cli_file_long_option_file_no_argument(self) -> None:
        """Test cli --file option with no argument."""
        self.assert_command(
            cli,
            ['cli', '--file'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_parse_error(self) -> None:
        self.assert_command(
            cli,
            ['cli', '-f', 'test/parse-error.xml'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: test/parse-error.xml: failed to parse file: no element found: line 1, column 0\n'
            # pylint: enable=line-too-long
        )

    def test_cli_xml_parsing_error(self) -> None:
        self.assert_command(
            cli,
            ['cli', '-f', 'test/xml-parsing-error.xml'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: test/xml-parsing-error.xml: unexpected element tag \'badtag\'\n'
            # pylint: enable=line-too-long
        )

    def test_cli_invalid_subcommand(self) -> None:
        """Test cli with an invalid subcommand."""
        self.assert_command(
            cli,
            ['cli', 'unknown args'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                "cli: error: argument subcommand: invalid choice: 'unknown args' (choose from package, class, file)\n"
            )  # pylint: enable=line-too-long
        )

    def test_cli_empty_report(self) -> None:
        self.assert_command(
            cli,
            ['cli', '--file', 'test/empty.xml'],
            stdout='No classes found.\n'
        )

    def test_cli_package_subcommand(self) -> None:
        """Test cli with the package subcommand."""
        self.assert_command(
            cli,
            ['cli', 'package', 'test1'],
            stdout=(  # pylint: disable=line-too-long
                '┌──────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name         │ Branch          │ Line            │ Method          │\n'
                '├──────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test1.Class1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1.Class2 │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└──────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_no_args(self) -> None:
        """Test cli with the package subcommand with no arguments."""
        self.assert_command(
            cli,
            ['cli', 'package'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli package [-h] [-f FILE] [-l] [PACKAGE]\n'
                'cli package: error: the following arguments are required: PACKAGE\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_package_doesnt_exists(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', 'package_that_doesnt_exists'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: package \'package_that_doesnt_exists\' doesn\'t exists\n'
            # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_empty_package(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '-f', 'test/empty-package.xml', 'emptyPackage'],
            stdout='There is no class in this package.\n'
        )

    def test_cli_package_subcommand_unknows_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', 'test', '--unknown-option'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: unrecognized arguments: --unknown-option\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_help_short_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '-h'],
            stdout=self.help_package
        )

    def test_cli_package_subcommand_help_long_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '--help'],
            stdout=self.help_package
        )

    def test_cli_package_subcommand_file_doesnt_exists(self) -> None:
        """Test cli with the package subcommand with no report file."""
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'package', 'test1'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: target/site/jacoco/jacoco.xml: no such file or directory\n'
            # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_parse_error(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '-f', 'test/parse-error.xml', 'testPackage'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: test/parse-error.xml: failed to parse file: no element found: line 1, column 0\n'
            # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_file_short_option(self) -> None:
        """Test cli with the package subcommand with the -f option."""
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'package', '-f', 'test/jacoco.xml', 'test1'],
            stdout=(  # pylint: disable=line-too-long
                '┌──────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name         │ Branch          │ Line            │ Method          │\n'
                '├──────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test1.Class1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1.Class2 │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└──────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_file_short_option_file_doesnt_exists(
        self
    ) -> None:
        """Test cli with the package subcommand with the -f option with a file
        that doesn't exists."""
        self.assert_command(
            cli,
            ['cli', 'package', '-f', 'file.xml', 'packagename'],
            returncode=1,
            stderr='cli: error: file.xml: no such file or directory\n'
        )

    def test_cli_package_subcommand_file_short_option_file_no_argument(
        self
    ) -> None:
        """Test cli with the package subcommand with the -f option with no
        argument."""
        self.assert_command(
            cli,
            ['cli', 'package', '-f'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_file_long_option(self) -> None:
        """Test cli with the package subcommand with the --file option."""
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'package', '--file', 'test/jacoco.xml', 'test1'],
            stdout=(  # pylint: disable=line-too-long
                '┌──────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name         │ Branch          │ Line            │ Method          │\n'
                '├──────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test1.Class1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1.Class2 │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└──────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_file_long_option_file_doesnt_exists(
        self
    ) -> None:
        """Test cli with the package subcommand with the --file option with a
        file that doesn't exists."""
        self.assert_command(
            cli,
            ['cli', 'package', 'packageName', '--file', 'file.xml'],
            returncode=1,
            stderr='cli: error: file.xml: no such file or directory\n'
        )

    def test_cli_package_subcommand_file_long_option_file_no_argument(self
                                                                      ) -> None:
        """Test cli with the package subcommand with the --file option with no
        argument."""
        self.assert_command(
            cli,
            ['cli', 'package', '--file'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_package_subcommand_list_packages_short_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '-l'],
            stdout=(
                'test1\n'
                'test2\n'
            )
        )

    def test_cli_package_subcommand_list_packages_long_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '--list-packages'],
            stdout=(
                'test1\n'
                'test2\n'
            )
        )

    def test_cli_package_subcommand_list_packages_short_option_no_packages(
        self
    ) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '--file', 'test/empty.xml', '-l'],
        )

    def test_cli_package_subcommand_list_packages_long_option_no_packages(
        self
    ) -> None:
        self.assert_command(
            cli,
            ['cli', 'package', '--file', 'test/empty.xml', '--list-packages'],
        )

    def test_cli_class_subcommand(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', 'test1.Class1'],
            stdout=(  # pylint: disable=line-too-long
                '┌─────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name    │ Branch          │ Line            │ Method          │\n'
                '├─────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ <init>  │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method2 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method3 │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '└─────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_no_args(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'class'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli class [-h] [-f FILE] CLASS\n'
                'cli class: error: the following arguments are required: CLASS\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_class_doesnt_exists(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', 'package.ClassThatDoesntExists'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: class \'package.ClassThatDoesntExists\' doesn\'t exists\n'
            # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_help_short_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', '-h'],
            stdout=self.help_class
        )

    def test_cli_class_subcommand_help_long_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', '--help'],
            stdout=self.help_class
        )

    def test_cli_class_subcommand_file_doesnt_exists(self) -> None:
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'class', 'ClassName'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: target/site/jacoco/jacoco.xml: no such file or directory\n'
            # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_parse_error(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', '-f', 'test/parse-error.xml', 'testPackage.Class'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: test/parse-error.xml: failed to parse file: no element found: line 1, column 0\n'
            # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_class_empty(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', 'test.EmptyClass', '-f', 'test/empty-class.xml'],
            stdout='No methods found in this class.\n'
        )

    def test_cli_class_subcommand_file_short_option(self) -> None:
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'class', '-f', 'test/jacoco.xml', 'test1.Class1'],
            stdout=(  # pylint: disable=line-too-long
                '┌─────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name    │ Branch          │ Line            │ Method          │\n'
                '├─────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ <init>  │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method2 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method3 │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '└─────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_file_short_option_file_doesnt_exists(
        self
    ) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', '-f', 'file.xml', 'ClassName'],
            returncode=1,
            stderr='cli: error: file.xml: no such file or directory\n'
        )

    def test_cli_class_subcommand_file_short_option_file_no_argument(self
                                                                     ) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', '-f'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_file_long_option(self) -> None:
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'class', '--file', 'test/jacoco.xml', 'test1.Class1'],
            stdout=(  # pylint: disable=line-too-long
                '┌─────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name    │ Branch          │ Line            │ Method          │\n'
                '├─────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ <init>  │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method1 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method2 │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ method3 │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '└─────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_class_subcommand_file_long_option_file_doesnt_exists(self
                                                                      ) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', '--file', 'file.xml', 'ClassName'],
            returncode=1,
            stderr='cli: error: file.xml: no such file or directory\n'
        )

    def test_cli_class_subcommand_file_long_option_file_no_argument(self
                                                                    ) -> None:
        self.assert_command(
            cli,
            ['cli', 'class', '--file'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', 'test1/Class1.java'],
            stdout=(  # pylint: disable=line-too-long
                '┌───────────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name              │ Branch          │ Line            │ Method          │\n'
                '├───────────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test1/Class1.java │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '└───────────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_no_args(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file'],
            stdout=(  # pylint: disable=line-too-long
                '┌───────────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name              │ Branch          │ Line            │ Method          │\n'
                '├───────────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test2/Class1.java │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test2/Class2.java │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test1/Class1.java │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1/Class2.java │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└───────────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_help_short_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '-h'],
            stdout=self.help_file
        )

    def test_cli_file_subcommand_help_long_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '--help'],
            stdout=self.help_file
        )

    def test_cli_file_subcommand_file_doesnt_exists(self) -> None:
        """Test cli with the file subcommand with no report file."""
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'file'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: target/site/jacoco/jacoco.xml: no such file or directory\n'
            # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_parse_error(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '-f', 'test/parse-error.xml', 'TestFile.java'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: test/parse-error.xml: failed to parse file: no element found: line 1, column 0\n'
            # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_file_short_option(self) -> None:
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'file', '-f', 'test/jacoco.xml'],
            stdout=(  # pylint: disable=line-too-long
                '┌───────────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name              │ Branch          │ Line            │ Method          │\n'
                '├───────────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test2/Class1.java │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test2/Class2.java │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test1/Class1.java │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1/Class2.java │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└───────────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_file_short_option_file_doesnt_exists(self
                                                                      ) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '-f', 'file.xml'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: file.xml: no such file or directory\n'
            # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_file_short_option_file_no_argument(self
                                                                    ) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '-f'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_file_long_option(self) -> None:
        self.hide_file('target/site/jacoco/jacoco.xml')
        self.assert_command(
            cli,
            ['cli', 'file', '--file', 'test/jacoco.xml'],
            stdout=(  # pylint: disable=line-too-long
                '┌───────────────────┬─────────────────┬─────────────────┬─────────────────┐\n'
                '│ Name              │ Branch          │ Line            │ Method          │\n'
                '├───────────────────┼─────────────────┼─────────────────┼─────────────────┤\n'
                '│ test2/Class1.java │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test2/Class2.java │ \x1b[30m━━━━━━━━━━\x1b[0m  n/a │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │ \x1b[31m━━━━━━━━━━\x1b[0m   0% │\n'
                '│ test1/Class1.java │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │ \x1b[32m━━━━━━━━━━\x1b[0m 100% │\n'
                '│ test1/Class2.java │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  50% │ \x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  60% │ \x1b[32m━━━━━━━\x1b[31m╺━━\x1b[0m  75% │\n'
                '└───────────────────┴─────────────────┴─────────────────┴─────────────────┘\n'
            )  # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_file_long_option_file_doesnt_exists(self
                                                                     ) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '--file', 'file.xml'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: file.xml: no such file or directory\n'
            # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_file_long_option_file_no_argument(self
                                                                   ) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '--file'],
            returncode=1,
            stderr=(  # pylint: disable=line-too-long
                'usage: cli [-h] [-f FILE] [-v] {package,class,file} ...\n'
                'cli: error: argument -f/--file: expected one argument\n'
            )  # # pylint: enable=line-too-long
        )

    def test_cli_file_subcommand_list_files_short_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '-l'],
            stdout=(
                'test1/Class1.java\n'
                'test1/Class2.java\n'
                'test2/Class1.java\n'
                'test2/Class2.java\n'
            )
        )

    def test_cli_file_subcommand_list_files_long_option(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', '--list-files'],
            stdout=(
                'test1/Class1.java\n'
                'test1/Class2.java\n'
                'test2/Class1.java\n'
                'test2/Class2.java\n'
            )
        )

    def test_cli_file_subcommand_source_file_doesnt_exists(self) -> None:
        self.assert_command(
            cli,
            ['cli', 'file', 'FileThatDoesntExists.java'],
            returncode=1,
            # pylint: disable=line-too-long
            stderr='cli: error: file \'FileThatDoesntExists.java\' doesn\'t exists\n'
            # pylint: enable=line-too-long
        )
