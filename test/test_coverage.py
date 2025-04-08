from unittest import TestCase
from xml.etree.ElementTree import fromstring

from jacoco_summary.column_name import ColumnName
from jacoco_summary.coverage import Coverage


class TestCoverage(TestCase):

    def test_create_coverage(self) -> None:
        coverage = Coverage('test coverage', 1, 2, 3, 4, 5, 6)
        self.assertEqual(coverage.name, 'test coverage')
        self.assertEqual(coverage.branch_missed, 1)
        self.assertEqual(coverage.branch_covered, 2)
        self.assertEqual(coverage.line_missed, 3)
        self.assertEqual(coverage.line_covered, 4)
        self.assertEqual(coverage.method_missed, 5)
        self.assertEqual(coverage.method_covered, 6)

    def test_create_coverage_default(self) -> None:
        coverage = Coverage('test coverage')
        self.assertEqual(coverage.name, 'test coverage')
        self.assertEqual(coverage.branch_missed, 0)
        self.assertEqual(coverage.branch_covered, 0)
        self.assertEqual(coverage.line_missed, 0)
        self.assertEqual(coverage.line_covered, 0)
        self.assertEqual(coverage.method_missed, 0)
        self.assertEqual(coverage.method_covered, 0)

    def test_from_xml_element(self) -> None:
        element = fromstring(
            '<class name="App" sourcefilename="App.java">\n'
            '    <method name="method1" desc="(I)V" line="9">\n'
            '        <counter type="INSTRUCTION" missed="0" covered="0"/>\n'
            '        <counter type="BRANCH" missed="0" covered="0"/>\n'
            '        <counter type="LINE" missed="0" covered="0"/>\n'
            '        <counter type="COMPLEXITY" missed="0" covered="0"/>\n'
            '        <counter type="METHOD" missed="0" covered="0"/>\n'
            '    </method>\n'
            '    <counter type="INSTRUCTION" missed="0" covered="1"/>\n'
            '    <counter type="BRANCH" missed="2" covered="3"/>\n'
            '    <counter type="LINE" missed="4" covered="5"/>\n'
            '    <counter type="COMPLEXITY" missed="6" covered="7"/>\n'
            '    <counter type="METHOD" missed="8" covered="9"/>\n'
            '    <counter type="CLASS" missed="10" covered="11"/>\n'
            '</class>\n'
        )
        coverage = Coverage.from_xml_element(element)
        self.assertEqual(coverage.name, 'App')
        self.assertEqual(coverage.branch_missed, 2)
        self.assertEqual(coverage.branch_covered, 3)
        self.assertEqual(coverage.line_missed, 4)
        self.assertEqual(coverage.line_covered, 5)
        self.assertEqual(coverage.method_missed, 8)
        self.assertEqual(coverage.method_covered, 9)

    def test_get_name(self) -> None:
        coverage = Coverage('test coverage', 1, 2, 3, 4, 5, 6)
        self.assertEqual(coverage.get_name(), 'test coverage')

    def test_get_field(self) -> None:
        coverage = Coverage('test coverage', 1, 2, 3, 4, 5, 6)
        self.assertEqual(coverage.get_field(ColumnName.NAME), 'test coverage')
        self.assertEqual(coverage.get_field(ColumnName.BRANCH),
                         '\x1b[32m━━━━━━\x1b[31m╺━━━\x1b[0m  67%')
        self.assertEqual(coverage.get_field(ColumnName.LINE),
                         '\x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  57%')
        self.assertEqual(coverage.get_field(ColumnName.METHOD),
                         '\x1b[32m━━━━━\x1b[31m╺━━━━\x1b[0m  55%')
        self.assertRaises(AssertionError, coverage.get_field, -1)
