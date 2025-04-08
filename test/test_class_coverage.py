from unittest import TestCase
from xml.etree.ElementTree import fromstring

from jacoco_summary.class_coverage import ClassCoverage
from jacoco_summary.method_coverage import MethodCoverage


class TestClassCoverage(TestCase):

    def setUp(self) -> None:
        self.class_coverage1 = ClassCoverage('ClassName1')
        self.class_coverage2 = ClassCoverage('packageName/ClassName2', 1, 2, 3,
                                             4, 5, 6,
                                             [MethodCoverage('method1')])
        self.class_coverage3 = ClassCoverage('packageName/ClassName3$SubClass',
                                             methods=[MethodCoverage('method1'),
                                                      MethodCoverage('method2')]
                                             )

    def test_create_class_coverage(self) -> None:
        self.assertEqual(self.class_coverage2.name, 'packageName/ClassName2')
        self.assertEqual(self.class_coverage2.branch_missed, 1)
        self.assertEqual(self.class_coverage2.branch_covered, 2)
        self.assertEqual(self.class_coverage2.line_missed, 3)
        self.assertEqual(self.class_coverage2.line_covered, 4)
        self.assertEqual(self.class_coverage2.method_missed, 5)
        self.assertEqual(self.class_coverage2.method_covered, 6)
        self.assertEqual(len(self.class_coverage2.methods), 1)
        self.assertEqual(len(self.class_coverage3.methods), 2)

    def test_create_class_coverage_default(self) -> None:
        self.assertEqual(self.class_coverage1.name, 'ClassName1')
        self.assertEqual(self.class_coverage1.branch_missed, 0)
        self.assertEqual(self.class_coverage1.branch_covered, 0)
        self.assertEqual(self.class_coverage1.line_missed, 0)
        self.assertEqual(self.class_coverage1.line_covered, 0)
        self.assertEqual(self.class_coverage1.method_missed, 0)
        self.assertEqual(self.class_coverage1.method_covered, 0)
        methods: list[MethodCoverage] = []
        self.assertEqual(self.class_coverage1.methods, methods)

    def test_create_from_xml_element(self) -> None:
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
        class_coverage = ClassCoverage.from_xml_element(element)
        self.assertEqual(class_coverage.name, 'App')
        self.assertEqual(class_coverage.branch_missed, 2)
        self.assertEqual(class_coverage.branch_covered, 3)
        self.assertEqual(class_coverage.line_missed, 4)
        self.assertEqual(class_coverage.line_covered, 5)
        self.assertEqual(class_coverage.method_missed, 8)
        self.assertEqual(class_coverage.method_covered, 9)
        self.assertEqual(len(class_coverage.methods), 1)

    def test_get_name(self) -> None:
        self.assertEqual(self.class_coverage1.get_name(), 'ClassName1')
        self.assertEqual(self.class_coverage2.get_name(),
                         'packageName.ClassName2')
        self.assertEqual(self.class_coverage3.get_name(),
                         'packageName.ClassName3.SubClass')
