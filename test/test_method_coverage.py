from unittest import TestCase
from xml.etree.ElementTree import fromstring

from jacoco_summary.method_coverage import MethodCoverage


class TestMethodCoverage(TestCase):

    def test_from_xml_element(self) -> None:
        element = fromstring(
            '    <method name="method1" desc="(I)V" line="9">\n'
            '        <counter type="INSTRUCTION" missed="0" covered="1"/>\n'
            '        <counter type="BRANCH" missed="2" covered="3"/>\n'
            '        <counter type="LINE" missed="4" covered="5"/>\n'
            '        <counter type="COMPLEXITY" missed="6" covered="7"/>\n'
            '        <counter type="METHOD" missed="8" covered="9"/>\n'
            '    </method>\n'
        )

        method_coverage = MethodCoverage.from_xml_element(element)
        self.assertEqual(method_coverage.name, 'method1')
        self.assertEqual(method_coverage.branch_missed, 2)
        self.assertEqual(method_coverage.branch_covered, 3)
        self.assertEqual(method_coverage.line_missed, 4)
        self.assertEqual(method_coverage.line_covered, 5)
        self.assertEqual(method_coverage.method_missed, 8)
        self.assertEqual(method_coverage.method_covered, 9)
