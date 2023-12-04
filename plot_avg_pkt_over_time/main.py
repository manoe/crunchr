#!/bin/python3

import math
import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np


def sum_list_prop(list_prop, run):
    return [sum([x[list_prop] for x in i['nodes'] if x['energy'] > 0 or not args.no_dead]) for i in run['nrg_list'] if i['timestamp'] > args.start_from]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_avg_pkt_over_time', description='Plot average pkt over time', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin', nargs='+')
    parser.add_argument('-d', '--no-dead', dest='no_dead', action='store_true')
    parser.add_argument('-f', '--from', dest='start_from', type=int, default=0)

    args = parser.parse_args()

    files = args.filename

    res = {}

    for file in files:
        stream = open(file, 'r')

        loader = yaml.safe_load(stream)
        res[file.split('/')[-1]] = np.average([np.subtract(i[1:], i[:-1])
                                    for i in [sum_list_prop('report_recv', run) for run in loader['runs']]], axis=0)

    ts = [i['timestamp'] for i in loader['runs'][0]['nrg_list'] if i['timestamp'] > args.start_from]
    ts = ts[1:]
    plt.plot(ts, np.transpose([res[i] for i in res.keys()]))
    plt.legend(res.keys())
    plt.show()
