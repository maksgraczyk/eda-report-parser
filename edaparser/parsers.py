import re
import io
from abc import ABC, abstractmethod
from pathlib import Path


class Parser(ABC):
    @abstractmethod
    def __init__(self, src):
        self._str = ''

        if isinstance(src, Path):
            with src.open(mode='r') as f:
                for line in f:
                    self._str += line
        elif isinstance(src, io.TextIOWrapper):
            for line in src:
                self._str += line
        elif isinstance(src, str):
            self._str = src
        else:
            raise RuntimeError('src must be of type either '
                               'pathlib.Path, io.TextIOWrapper, '
                               'or str')

    @abstractmethod
    def get_table(self):
        pass


class VivadoTableParser(Parser):
    def __init__(self, src):
        super().__init__(src)

    def get_table(self):
        matches = re.findall(r'\d+\. (.+?)\n-+\n\n([\+-\| \S\n]+?)\n\n',
                             self._str)

        tables = []

        for section_name, table in matches:
            final_table_lines = []
            for line in table.split('\n'):
                if line.startswith('+') or line.startswith('|'):
                    final_table_lines.append(line)

            tables.append((section_name, final_table_lines))

        result = {}

        for section_name, table_lines in tables:
            parsed_table = []

            for line in table_lines:
                if re.match(r'^[\+\-]+$', line):
                    parsed_table.append(None)
                else:
                    row_elements = filter(lambda x: len(x) > 0,
                                          map(str.strip, line.split(' | ')))
                    parsed_table.append(list(row_elements))

            result[section_name] = parsed_table

        return result
