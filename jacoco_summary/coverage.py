from __future__ import annotations

from xml.etree.ElementTree import Element

from .column_name import ColumnName
from .counter_type import CounterType
from .utils import percentage_bar


class Coverage:

    def __init__(
        self,
        name: str,
        branch_missed: int = 0,
        branch_covered: int = 0,
        line_missed: int = 0,
        line_covered: int = 0,
        method_missed: int = 0,
        method_covered: int = 0
    ) -> None:
        self.name = name
        self.branch_missed = branch_missed
        self.branch_covered = branch_covered
        self.line_missed = line_missed
        self.line_covered = line_covered
        self.method_missed = method_missed
        self.method_covered = method_covered

    @classmethod
    def from_xml_element(cls, element: Element) -> Coverage:
        branch_missed: int = 0
        branch_covered: int = 0
        line_missed: int = 0
        line_covered: int = 0
        method_missed: int = 0
        method_covered: int = 0

        for child in element:
            if child.tag != 'counter':
                continue

            counter_type = CounterType(child.attrib['type'])
            match counter_type:
                case CounterType.BRANCH:
                    branch_missed = int(child.attrib['missed'])
                    branch_covered = int(child.attrib['covered'])

                case CounterType.LINE:
                    line_missed = int(child.attrib['missed'])
                    line_covered = int(child.attrib['covered'])

                case CounterType.METHOD:
                    method_missed = int(child.attrib['missed'])
                    method_covered = int(child.attrib['covered'])

                case _:
                    pass

        return cls(
            element.attrib['name'],
            branch_missed,
            branch_covered,
            line_missed,
            line_covered,
            method_missed,
            method_covered
        )

    def get_name(self) -> str:
        return self.name

    def get_field(self, column_name: ColumnName) -> str:
        match column_name:
            case ColumnName.NAME:
                return self.get_name()

            case ColumnName.BRANCH:
                return percentage_bar(self.branch_missed, self.branch_covered)

            case ColumnName.LINE:
                return percentage_bar(self.line_missed, self.line_covered)

            case ColumnName.METHOD:
                return percentage_bar(self.method_missed, self.method_covered)

            case _:
                assert False, 'unreachable'
