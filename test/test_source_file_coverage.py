from unittest import TestCase
from xml.etree.ElementTree import fromstring

from jacoco_summary.source_file_coverage import SourceFileCoverage


class TestSourceFileCoverage(TestCase):

    def test_create_from_xml_file(self) -> None:
        element = fromstring(
            '<sourcefile name="Class1.java">\n'
            '    <line nr="5" mi="0" ci="2" mb="0" cb="0"/>\n'
            '    <line nr="6" mi="0" ci="1" mb="0" cb="0"/>\n'
            '    <counter type="INSTRUCTION" missed="0" covered="1"/>\n'
            '    <counter type="BRANCH" missed="2" covered="3"/>\n'
            '    <counter type="LINE" missed="4" covered="5"/>\n'
            '    <counter type="COMPLEXITY" missed="6" covered="7"/>\n'
            '    <counter type="METHOD" missed="8" covered="9"/>\n'
            '    <counter type="CLASS" missed="10" covered="11"/>\n'
            '</sourcefile>\n'
        )
        coverage = SourceFileCoverage.from_xml_element(element)
        self.assertEqual(coverage.name, 'Class1.java')
        self.assertEqual(coverage.branch_missed, 2)
        self.assertEqual(coverage.branch_covered, 3)
        self.assertEqual(coverage.line_missed, 4)
        self.assertEqual(coverage.line_covered, 5)
        self.assertEqual(coverage.method_missed, 8)
        self.assertEqual(coverage.method_covered, 9)
