from __future__ import annotations

from xml.etree.ElementTree import Element

from .coverage import Coverage


class MethodCoverage(Coverage):

    @classmethod
    def from_xml_element(cls, element: Element) -> MethodCoverage:
        base_instance = super().from_xml_element(element)
        return cls(
            base_instance.name,
            base_instance.branch_missed,
            base_instance.branch_covered,
            base_instance.line_missed,
            base_instance.line_covered,
            base_instance.method_missed,
            base_instance.method_covered
        )
