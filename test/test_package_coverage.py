from xml.etree.ElementTree import fromstring
from unittest import TestCase

from jacoco_summary.class_coverage import ClassCoverage
from jacoco_summary.package_coverage import PackageCoverage
from jacoco_summary.source_file_coverage import SourceFileCoverage
from jacoco_summary.xml_parsing_exception import XmlParsingException


class TestPackageCoverage(TestCase):

    def setUp(self) -> None:
        self.class1 = ClassCoverage('Class1')
        self.class2 = ClassCoverage('Class2')
        self.source_file1 = SourceFileCoverage('Class1.java')
        self.source_file2 = SourceFileCoverage('Class2.java')
        self.package = PackageCoverage(
            'package1',
            0,
            1,
            2,
            3,
            4,
            5,
            classes=[self.class1, self.class2],
            source_files=[self.source_file1, self.source_file2]
        )

    def test_create_package_coverage(self) -> None:
        self.assertEqual(self.package.name, 'package1')
        self.assertEqual(self.package.branch_missed, 0)
        self.assertEqual(self.package.branch_covered, 1)
        self.assertEqual(self.package.line_missed, 2)
        self.assertEqual(self.package.line_covered, 3)
        self.assertEqual(self.package.method_missed, 4)
        self.assertEqual(self.package.method_covered, 5)
        self.assertEqual(len(self.package.classes), 2)
        self.assertIn(self.class1, self.package.classes)
        self.assertIn(self.class2, self.package.classes)
        self.assertEqual(len(self.package.source_files), 2)
        self.assertIn(self.source_file1, self.package.source_files)
        self.assertIn(self.source_file1, self.package.source_files)

    def test_from_xml_emement(self) -> None:
        element = fromstring(
            '<package name="package1">\n'
            '    <class name="package1/Class1" sourcefilename="Class1.java">\n'
            '    </class>\n'
            '    <class name="package1/Class2" sourcefilename="Class2.java">\n'
            '    </class>\n'
            '    <sourcefile name="Class1.java">\n'
            '    </sourcefile>\n'
            '    <sourcefile name="Class2.java">\n'
            '    </sourcefile>\n'
            '    <counter type="INSTRUCTION" missed="0" covered="1"/>\n'
            '    <counter type="BRANCH" missed="2" covered="3"/>\n'
            '    <counter type="LINE" missed="4" covered="5"/>\n'
            '    <counter type="COMPLEXITY" missed="6" covered="7"/>\n'
            '    <counter type="METHOD" missed="8" covered="9"/>\n'
            '    <counter type="CLASS" missed="10" covered="11"/>\n'
            '</package>\n'
        )
        coverage = PackageCoverage.from_xml_element(element)
        self.assertEqual(coverage.name, 'package1')
        self.assertEqual(coverage.branch_missed, 2)
        self.assertEqual(coverage.branch_covered, 3)
        self.assertEqual(coverage.line_missed, 4)
        self.assertEqual(coverage.line_covered, 5)
        self.assertEqual(coverage.method_missed, 8)
        self.assertEqual(coverage.method_covered, 9)
        self.assertEqual(len(coverage.classes), 2)
        self.assertEqual(len(coverage.source_files), 2)

    def test_from_xml_element_raises_xml_parsing_exception(self) -> None:
        element = fromstring(
            '<package name="package1">\n'
            '    <badtag/>\n'
            '</package>\n'
        )
        with self.assertRaises(XmlParsingException) as cm:
            PackageCoverage.from_xml_element(element)
        self.assertEqual(str(cm.exception), "unexpected element tag 'badtag'")

    def test_create_package_coverage_default(self) -> None:
        coverage = PackageCoverage('package2')
        self.assertEqual(coverage.name, 'package2')
        self.assertEqual(coverage.branch_missed, 0)
        self.assertEqual(coverage.branch_covered, 0)
        self.assertEqual(coverage.line_missed, 0)
        self.assertEqual(coverage.line_covered, 0)
        self.assertEqual(coverage.method_missed, 0)
        self.assertEqual(coverage.method_covered, 0)
        classes: list[ClassCoverage] = []
        self.assertEqual(coverage.classes, classes)
        source_files: list[SourceFileCoverage] = []
        self.assertEqual(coverage.source_files, source_files)

    def test_get_name(self) -> None:
        self.assertEqual(PackageCoverage('fr/domain/packageName').get_name(),
                         'fr.domain.packageName')

    def test_get_class(self) -> None:
        self.assertIs(self.package.get_class('Class1'), self.class1)
        self.assertIs(self.package.get_class('Class2'), self.class2)
        self.assertIsNone(self.package.get_class('Class3'))
