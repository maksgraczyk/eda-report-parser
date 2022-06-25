import argparse
import sys
from pathlib import Path


PROG_NAME = 'reporthtml'


def error(msg):
    print(f'{PROG_NAME}: error: {msg}', file=sys.stderr)
    sys.exit(1)


def run(files, device, tool, output):
    src_report_strs = {}
    types = []

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
        types.append(path.stem)

    report_template = ''

    with (Path(__file__).parent / 'reporthtml.html').open(mode='r') as f:
        for line in f:
            report_template += line

    substitutions = {
        '{DEVICE NAME}': device
    }

    types_strs = []

    for t in types:
        types_strs.append(f'<option value="{t}">{t}</option>')

    substitutions['{TYPES}'] = '\n          '.join(types_strs)

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
