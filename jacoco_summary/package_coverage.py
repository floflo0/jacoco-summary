from __future__ import annotations

from xml.etree.ElementTree import Element

from .class_coverage import ClassCoverage
from .coverage import Coverage
from .source_file_coverage import SourceFileCoverage
from .xml_parsing_exception import XmlParsingException


class PackageCoverage(Coverage):

    def __init__(
        self,
        name: str,
        branch_missed: int = 0,
        branch_covered: int = 0,
        line_missed: int = 0,
        line_covered: int = 0,
        method_missed: int = 0,
        method_covered: int = 0,
        classes: list[ClassCoverage] = None,
        source_files: list[SourceFileCoverage] = None
    ) -> None:
        super().__init__(
            name,
            branch_missed,
            branch_covered,
            line_missed,
            line_covered,
            method_missed,
            method_covered
        )
        if classes is None:
            classes = []
        self.classes = classes
        if source_files is None:
            source_files = []
        self.source_files = source_files

    @classmethod
    def from_xml_element(cls, element: Element) -> PackageCoverage:
        base_instance = super().from_xml_element(element)

        classes: list[ClassCoverage] = []
        source_files: list[SourceFileCoverage] = []
        for child in element:
            if child.tag == 'class':
                classes.append(ClassCoverage.from_xml_element(child))
                continue

            if child.tag == 'sourcefile':
                source_files.append(SourceFileCoverage.from_xml_element(child))
                source_files[-1].name = \
                                 f'{base_instance.name}/{source_files[-1].name}'
                continue

            if child.tag == 'counter':
                # parsed by Coverage
                continue

            raise XmlParsingException(child)

        return cls(
            base_instance.name,
            base_instance.branch_missed,
            base_instance.branch_covered,
            base_instance.line_missed,
            base_instance.line_covered,
            base_instance.method_missed,
            base_instance.method_covered,
            classes,
            source_files
        )

    def get_name(self) -> str:
        return self.name.replace('/', '.')

    def get_class(self, class_name: str) -> ClassCoverage | None:
        for java_class in self.classes:
            if java_class.get_name() == class_name:
                return java_class

        return None
