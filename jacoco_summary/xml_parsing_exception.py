from xml.etree.ElementTree import Element


class XmlParsingException(Exception):

    def __init__(self, element: Element) -> None:
        super().__init__(f'unexpected element tag {repr(element.tag)}')
