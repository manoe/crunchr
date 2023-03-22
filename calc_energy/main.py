#!/bin/python3
import argparse
import errno

import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx
# import scipy as sp


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pdr_hop_stat', description='Parse protocol logs and calculate pdr', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-d', '--data',
                        action='store_true', dest='data')
    parser.add_argument('-n', '--no-header',
                        action='store_true', dest='no_header')
    parser.add_argument('-g', '--gap', dest='gap')
    parser.add_argument('-s', '--sheet',
                        action='store_true', dest='sheet')
    parser.add_argument('-r', '--remove-outlier',
                        action='store_true', dest='remove_outlier')

    parser.add_argument('filename')

    args = parser.parse_args()
    stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    runs = loader['runs']

    spent_nrg = []

    for run in runs:
        for i in run['loc_pdr']:
            if 'spent_energy' in i:
                spent_nrg.append(i['spent_energy'])

    if args.remove_outlier:
        spent_nrg = reject_outliers(np.array(spent_nrg))

    print('avg.nrg: ' + str(np.average(spent_nrg)))
    print('std.nrg: ' + str(np.std(spent_nrg)))

