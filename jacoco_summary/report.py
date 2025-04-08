from __future__ import annotations

from xml.etree.ElementTree import Element, parse

from .class_coverage import ClassCoverage
from .coverage import Coverage
from .package_coverage import PackageCoverage
from .source_file_coverage import SourceFileCoverage
from .xml_parsing_exception import XmlParsingException


class Report(Coverage):

    def __init__(
        self,
        name: str,
        branch_missed: int = 0,
        branch_covered: int = 0,
        line_missed: int = 0,
        line_covered: int = 0,
        method_missed: int = 0,
        method_covered: int = 0,
        packages: list[PackageCoverage] = None,
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
        if packages is None:
            packages = []
        self.packages = packages

    @classmethod
    def from_xml_file(cls, xml_file_path: str) -> Report:
        # Raises PArse Error
        tree = parse(xml_file_path)
        root: Element = tree.getroot()
        if root.tag != 'report':
            raise XmlParsingException(root)
        return cls.from_xml_element(root)

    @classmethod
    def from_xml_element(cls, element: Element) -> Report:
        base_instance = super().from_xml_element(element)

        packages: list[PackageCoverage] = []
        for child in element:
            if child.tag == 'package':
                packages.append(PackageCoverage.from_xml_element(child))
                continue

            if child.tag == 'sessioninfo':
                # ignore this tag
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
            packages
        )

    def get_class(self, class_name: str) -> ClassCoverage | None:
        for package in self.packages:
            java_class = package.get_class(class_name)
            if java_class is not None:
                return java_class

        return None

    def get_classes(self) -> list[ClassCoverage]:
        """Return all the class in the packages of the report."""
        return [java_class
                for package in self.packages
                for java_class in package.classes]

    def get_package(self, package_name: str) -> PackageCoverage | None:
        for package in self.packages:
            if package.get_name() == package_name:
                return package
        return None

    def get_packages_names(self) -> list[str]:
        """Return the list of the packages's name in the report."""
        return [package.get_name() for package in self.packages]

    def get_source_file(self, file_name: str) -> SourceFileCoverage | None:
        for package in self.packages:
            for file in package.source_files:
                if file_name == file.name:
                    return file
        return None

    def get_source_files(self) -> list[SourceFileCoverage]:
        return [
            file
            for package in self.packages
            for file in package.source_files
        ]

    def get_source_files_names(self) -> list[str]:
        return [file.name for file in self.get_source_files()]
