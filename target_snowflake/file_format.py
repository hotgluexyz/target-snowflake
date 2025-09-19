"""Enums used by pipelinewise-target-snowflake"""
from enum import Enum, unique
from types import ModuleType
from typing import Callable

import target_snowflake.file_formats
from target_snowflake.exceptions import FileFormatNotFoundException, InvalidFileFormatException

# Supported types for file formats.
@unique
class FileFormatTypes(str, Enum):
    """Enum of supported file format types"""

    CSV = 'csv'
    PARQUET = 'parquet'

    @staticmethod
    def list():
        """List of supported file type values"""
        return list(map(lambda c: c.value, FileFormatTypes))


# pylint: disable=too-few-public-methods
class FileFormat:
    """File Format class"""

    def __init__(self, file_format: str, query_fn: Callable, file_format_type: FileFormatTypes=None, logger = None, connection_config = None):
        """Find the file format in Snowflake, detect its type and
        initialise file format specific functions"""

        if file_format_type:
            self.file_format_type = file_format_type
        else:
            # use CSV as default file format type
            self.file_format_type = FileFormatTypes.CSV

        self.formatter = self._get_formatter(self.file_format_type)
        self.logger = logger
        self.connection_config = connection_config
        delimiter = self.connection_config.get('delimiter', ',')

        if delimiter == "\\x1F":
            delimiter = '\x1F'

        # check if file_format exists
        file_formats_in_sf = query_fn(f"SHOW FILE FORMATS")
        self.logger.info(f"File formats in Snowflake: {file_formats_in_sf}")

        existing_file_format = next((fmt for fmt in file_formats_in_sf if fmt['name'] == file_format.split('.')[-1]), None)
        if not existing_file_format:
            self.logger.info(f"Format '{file_format}' not found, Auto creating file format")
            query_fn(f"""CREATE OR REPLACE FILE FORMAT {file_format}
                TYPE = 'CSV'
                TIMESTAMP_FORMAT = 'YYYY-MM-DD"T"HH24:MI:SS.FF6Z'
                FIELD_DELIMITER = '{delimiter}'
                NULL_IF = ('null', 'NULL', '')
                EMPTY_FIELD_AS_NULL = TRUE
                ESCAPE = NONE
                ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE""")
            self.logger.info(f"File format '{file_format}' created")
        else:
            # if file format exists, detect its type
            self.file_format_type = self._detect_file_format_type(file_format, query_fn)

    @classmethod
    def _get_formatter(cls, file_format_type: FileFormatTypes) -> ModuleType:
        """Get the corresponding file formatter implementation based
        on the FileFormatType parameter

        Params:
            file_format_type: FileFormatTypes enum item

        Returns:
            ModuleType implementation of the file ormatter
        """
        formatter = None

        if file_format_type == FileFormatTypes.CSV:
            formatter = target_snowflake.file_formats.csv
        elif file_format_type == FileFormatTypes.PARQUET:
            formatter = target_snowflake.file_formats.parquet
        else:
            raise InvalidFileFormatException(f"Not supported file format: '{file_format_type}")

        return formatter

    @classmethod
    def _detect_file_format_type(cls, file_format: str, query_fn: Callable) -> FileFormatTypes:
        """Detect the type of an existing snowflake file format object

        Params:
            file_format: File format name
            query_fn: A callable function that can run SQL queries in an active Snowflake session

        Returns:
            FileFormatTypes enum item
        """
        file_format_name = file_format.split('.')[-1]
        file_formats_in_sf = query_fn(f"SHOW FILE FORMATS LIKE '{file_format_name}'")

        if len(file_formats_in_sf) == 1:
            file_format = file_formats_in_sf[0]
            try:
                file_format_type = FileFormatTypes(file_format['type'].lower())
            except ValueError as ex:
                raise InvalidFileFormatException(
                    f"Not supported named file format {file_format_name}. Supported file formats: {FileFormatTypes}") \
                    from ex
        else:
            raise FileFormatNotFoundException(
                f"Named file format not found: {file_format}")

        return file_format_type
