from unittest import TestCase
from xml.etree.ElementTree import fromstring, ParseError

from jacoco_summary.class_coverage import ClassCoverage
from jacoco_summary.report import Report
from jacoco_summary.package_coverage import PackageCoverage
from jacoco_summary.source_file_coverage import SourceFileCoverage
from jacoco_summary.xml_parsing_exception import XmlParsingException


class TestReport(TestCase):

    def setUp(self) -> None:
        self.class1 = ClassCoverage('Class1')
        self.class2 = ClassCoverage('Class2')
        self.class3 = ClassCoverage('Class3')
        self.source_file1 = SourceFileCoverage('Class1.java')
        self.source_file2 = SourceFileCoverage('Class2.java')
        self.source_file3 = SourceFileCoverage('Class3.java')
        self.package1 = PackageCoverage(
            'package1',
            classes=[self.class1, self.class2],
            source_files=[self.source_file1, self.source_file2]
        )
        self.package2 = PackageCoverage(
            'package2',
            classes=[self.class3],
            source_files=[self.source_file3]
        )
        self.report = Report('reportName', 0, 1, 2, 3, 4, 5, packages=[
            self.package1,
            self.package2
        ])

    def test_create_report(self) -> None:
        self.assertEqual(self.report.name, 'reportName')
        self.assertEqual(self.report.branch_missed, 0)
        self.assertEqual(self.report.branch_covered, 1)
        self.assertEqual(self.report.line_missed, 2)
        self.assertEqual(self.report.line_covered, 3)
        self.assertEqual(self.report.method_missed, 4)
        self.assertEqual(self.report.method_covered, 5)
        self.assertEqual(len(self.report.packages), 2)
        self.assertIn(self.package1, self.report.packages)
        self.assertIn(self.package2, self.report.packages)

    def test_create_report_default(self) -> None:
        report = Report('reportName')
        self.assertEqual(report.name, 'reportName')
        self.assertEqual(report.branch_missed, 0)
        self.assertEqual(report.branch_covered, 0)
        self.assertEqual(report.line_missed, 0)
        self.assertEqual(report.line_covered, 0)
        self.assertEqual(report.method_missed, 0)
        self.assertEqual(report.method_covered, 0)
        packages: list[PackageCoverage] = []
        self.assertEqual(report.packages, packages)

    def test_from_xml_file(self) -> None:
        report = Report.from_xml_file('test/jacoco.xml')
        self.assertEqual(report.branch_missed, 6)
        self.assertEqual(report.branch_covered, 6)
        self.assertEqual(report.line_missed, 15)
        self.assertEqual(report.line_covered, 16)
        self.assertEqual(report.method_missed, 6)
        self.assertEqual(report.method_covered, 7)
        self.assertEqual(len(report.packages), 2)

    def test_from_xml_file_empty(self) -> None:
        report = Report.from_xml_file('test/empty.xml')
        self.assertEqual(report.branch_missed, 0)
        self.assertEqual(report.branch_covered, 0)
        self.assertEqual(report.line_missed, 0)
        self.assertEqual(report.line_covered, 0)
        self.assertEqual(report.method_missed, 0)
        self.assertEqual(report.method_covered, 0)
        packages: list[PackageCoverage] = []
        self.assertEqual(report.packages, packages)

    def test_from_xml_file_no_report_tag(self) -> None:
        with self.assertRaises(XmlParsingException) as cm:
            Report.from_xml_file('test/no-report.xml')
        self.assertEqual(str(cm.exception), "unexpected element tag 'test'")

    def test_from_xml_file_parse_error(self) -> None:
        self.assertRaises(
            ParseError,
            lambda: Report.from_xml_file('test/parse-error.xml')
        )

    def test_from_xml_element(self) -> None:
        element = fromstring(
            '<report name="test_project">\n'
            '    <sessioninfo id="sessionid" start="0" dump="0"/>\n'
            '    <package name="package1">\n'
            '        <counter type="INSTRUCTION" missed="0" covered="0"/>\n'
            '        <counter type="BRANCH" missed="0" covered="0"/>\n'
            '        <counter type="LINE" missed="0" covered="0"/>\n'
            '        <counter type="COMPLEXITY" missed="0" covered="0"/>\n'
            '        <counter type="METHOD" missed="0" covered="0"/>\n'
            '    </package>\n'
            '    <counter type="INSTRUCTION" missed="0" covered="1"/>\n'
            '    <counter type="BRANCH" missed="2" covered="3"/>\n'
            '    <counter type="LINE" missed="4" covered="5"/>\n'
            '    <counter type="COMPLEXITY" missed="6" covered="7"/>\n'
            '    <counter type="METHOD" missed="8" covered="9"/>\n'
            '    <counter type="CLASS" missed="10" covered="11"/>\n'
            '</report>\n'
        )
        report = Report.from_xml_element(element)
        self.assertEqual(report.name, 'test_project')
        self.assertEqual(report.branch_missed, 2)
        self.assertEqual(report.branch_covered, 3)
        self.assertEqual(report.line_missed, 4)
        self.assertEqual(report.line_covered, 5)
        self.assertEqual(report.method_missed, 8)
        self.assertEqual(report.method_covered, 9)
        self.assertEqual(len(report.packages), 1)

    def test_from_xml_element_raises_xml_parsing_exception(self) -> None:
        element = fromstring(
            '<report name="test_project">\n'
            '    <badtag/>\n'
            '</report>\n'
        )
        with self.assertRaises(XmlParsingException) as cm:
            Report.from_xml_element(element)
        self.assertEqual(str(cm.exception), "unexpected element tag 'badtag'")

    def test_get_class(self) -> None:
        self.assertIs(self.report.get_class('Class1'), self.class1)
        self.assertIs(self.report.get_class('Class2'), self.class2)
        self.assertIs(self.report.get_class('Class3'), self.class3)
        self.assertIsNone(self.report.get_class('Class4'))

    def test_get_classes(self) -> None:
        classes = self.report.get_classes()
        self.assertEqual(len(classes), 3)
        self.assertIn(self.class1, classes)
        self.assertIn(self.class2, classes)
        self.assertIn(self.class3, classes)

    def test_get_package(self) -> None:
        self.assertIs(self.report.get_package('package1'), self.package1)
        self.assertIs(self.report.get_package('package2'), self.package2)
        self.assertIsNone(self.report.get_package('package3'))

    def test_get_packages_names(self) -> None:
        expected_packages = ['package1', 'package2']
        self.assertEqual(self.report.get_packages_names(), expected_packages)

    def test_get_source_file(self) -> None:
        self.assertIs(self.report.get_source_file('Class1.java'),
                      self.source_file1)
        self.assertIs(self.report.get_source_file('Class2.java'),
                      self.source_file2)
        self.assertIs(self.report.get_source_file('Class3.java'),
                      self.source_file3)
        self.assertIsNone(self.report.get_source_file('source_file3'))

    def test_get_source_files(self) -> None:
        source_files = self.report.get_source_files()
        self.assertEqual(len(source_files), 3)
        self.assertIn(self.source_file1, source_files)
        self.assertIn(self.source_file2, source_files)
        self.assertIn(self.source_file3, source_files)

    def test_get_source_files_names(self) -> None:
        expected_source_files = ['Class1.java', 'Class2.java', 'Class3.java']
        self.assertEqual(self.report.get_source_files_names(),
                         expected_source_files)
