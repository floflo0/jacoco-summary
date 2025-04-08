from __future__ import annotations

import re
from xml.etree.ElementTree import Element

from .coverage import Coverage
from .method_coverage import MethodCoverage


class ClassCoverage(Coverage):

    def __init__(
        self,
        name: str,
        branch_missed: int = 0,
        branch_covered: int = 0,
        line_missed: int = 0,
        line_covered: int = 0,
        method_missed: int = 0,
        method_covered: int = 0,
        methods: list[MethodCoverage] = None
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
        if methods is None:
            methods = []
        self.methods = methods

    @classmethod
    def from_xml_element(cls, element: Element) -> ClassCoverage:
        base_instance = super().from_xml_element(element)

        methods: list[MethodCoverage] = []
        for child in element:
            if child.tag == 'method':
                methods.append(MethodCoverage.from_xml_element(child))

        return cls(
            base_instance.name,
            base_instance.branch_missed,
            base_instance.branch_covered,
            base_instance.line_missed,
            base_instance.line_covered,
            base_instance.method_missed,
            base_instance.method_covered,
            methods
        )

    def get_name(self) -> str:
        return re.sub(r'[\$\/]', '.', self.name)
