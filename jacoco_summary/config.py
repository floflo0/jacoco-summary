from .column_name import ColumnName


JACOCO_XML_FILE_PATH: str = 'target/site/jacoco/jacoco.xml'
CSV_SEPARATOR: str = ','

COLUMNS_ORDER: list[ColumnName] = [
    ColumnName.NAME,
    ColumnName.BRANCH,
    ColumnName.LINE,
    ColumnName.METHOD,
]
