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

        def count_spaces(string):
            cnt = 0

            for letter in string[1:]:
                if letter == ' ':
                    cnt += 1
                else:
                    break

            return cnt

        for section_name, table_lines in tables:
            parsed_table, children = [], {}

            orig_space_level = None
            cur_space_level = None
            last_space_index = []

            for line in table_lines:
                if not re.match(r'^[\+\-]+$', line):
                    i = len(parsed_table)

                    row_elements = \
                        list(map(str.strip, line.split(' |')))[:-1]
                    spaces_cnt = count_spaces(row_elements[0])

                    if i > 0:
                        if cur_space_level is None:
                            cur_space_level = spaces_cnt
                            orig_space_level = spaces_cnt
                            last_space_index.append(i)
                        elif spaces_cnt > cur_space_level:
                            cur_space_level = spaces_cnt
                            last_space_index.append(i)
                        elif spaces_cnt < cur_space_level:
                            cur_space_level = spaces_cnt
                            last_space_index.pop()
                            last_space_index[-1] = i
                        else:
                            last_space_index[-1] = i

                        if cur_space_level > orig_space_level:
                            children[i] = last_space_index[-2]

                    row_elements[0] = row_elements[0][spaces_cnt + 1:]

                    for i in range(len(row_elements)):
                        if len(row_elements[i]) == 0:
                            row_elements[i] = None

                    parsed_table.append(row_elements)

            result[section_name] = (parsed_table, children)

        return result
