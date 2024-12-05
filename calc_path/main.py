#!/bin/env python3
import argparse
import errno
import yaml
import numpy as np
import sys


def get_data_from_loader(top):
    if 'runs' in top:
        return top['runs'][0]['loc_pdr']
    else:
        return top


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='calc_path', description='Calculate path related stats', epilog=':-(')
    parser.add_argument('filename')

    args = parser.parse_args()
    stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    run = get_data_from_loader(loader)

    paths = [ sum( [ len(e['routing_table']) for e in i['engines']  if 'routing_table' in e and e['role'] == 'external' ] ) for i in run]

    print('avg.nrg: ' + str(np.average(paths)))
    print('std.nrg: ' + str(np.std(paths)))

