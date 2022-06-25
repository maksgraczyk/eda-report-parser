import argparse
import sys
from pathlib import Path
from tabulate import tabulate


PROG_NAME = 'reporthtml'


def error(msg):
    print(f'{PROG_NAME}: error: {msg}', file=sys.stderr)
    sys.exit(1)


def run(files, device, tool, output):
    # Setting things up
    src_report_strs = {}

    for path in files:
        if not path.exists():
            print(f'{str(path)} does not exist, skipping',
                  file=sys.stderr)
            continue

        string = ''
        with path.open(mode='r') as f:
            for line in f:
                string += line

        src_report_strs[path.stem] = string

    report_template = ''

    with (Path(__file__).parent / 'reporthtml.html').open(mode='r') as f:
        for line in f:
            report_template += line

    substitutions = {
        '{DEVICE NAME}': device
    }

    # Preparing a substitution for {TYPES}
    types_strs = []

    for t in src_report_strs.keys():
        types_strs.append(
            f'<option value="{t.replace(" ", "_")}">{t}</option>')

    substitutions['{TYPES}'] = '\n          '.join(types_strs)

    # Preparing a substitution for {TABLES}
    raw_tables = {}

    if tool == 'vivado':
        from edaparser import VivadoTableParser
        constr = VivadoTableParser

    for key, value in src_report_strs.items():
        parser = constr(value)
        raw_tables[key] = parser.get_table()

    table_divs = []

    for key, value in raw_tables.items():
        tables = []

        for section, (rows, children) in value.items():
            if len(rows) <= 1:
                continue

            table_str = tabulate(rows, headers='firstrow',
                                 tablefmt='html')
            table_str = table_str.replace('<table>',
                                          '<table class="interactive">')
            table_str = f'<h2>{section}</h2>\n' + table_str
            table_str = '<div class="section">\n' + table_str + '\n</div>'

            tables.append(table_str)

        div_str = \
            '<div style="display: none" ' + \
            f'id="{key.replace(" ", "_")}">\n' + \
            '\n'.join(tables) + '</div>'

        table_divs.append(div_str)

    substitutions['{TABLES}'] = '\n'.join(table_divs)

    # Writing the result to the output HTML file
    final_report = report_template

    for key, value in substitutions.items():
        final_report = final_report.replace(key, value)

    with output.open(mode='w') as f:
        f.write(final_report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROG_NAME,
                                     description='Produce an all-in-one HTML '
                                     'report from one or more text reports '
                                     'from EDA tools')
    parser.add_argument('files', metavar='REPORT', type=str,
                        nargs='+', help='one or more paths to text reports '
                        'from EDA tools')

    group = parser.add_argument_group('required arguments')
    group.add_argument('-d', metavar='NAME', type=str, dest='device',
                       help='name of the device analysed in the reports',
                       required=True)
    group.add_argument('-t', type=str, dest='tool',
                       help='EDA tool which has produced the reports',
                       choices=['vivado'], required=True)
    group.add_argument('-o', metavar='FILE', type=str, dest='output',
                       help='path to the output HTML file',
                       required=True)

    args = parser.parse_args()

    run(map(Path, args.files), args.device, args.tool, Path(args.output))
