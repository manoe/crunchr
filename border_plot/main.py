import yaml
import matplotlib.pyplot as plt
import argparse
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='border_plot', description='Plot MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    if 'runs' in loader:
        data = loader['runs'][0]['loc_pdr']
    else:
        data = loader['loc_pdr']

    borders = 