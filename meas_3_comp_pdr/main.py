#!/bin/env python3

import argparse
import logging
import matplotlib
from numpy.ma.extras import average

logger = logging.getLogger(__name__)
import sys
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib import cm
import numpy as np
import yaml

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='msr2mrp_meas_1_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='Input filename template, use $1 for protocol, $2 for seed as wildcard')
    parser.add_argument('-p1', '--proto1', dest='proto1', nargs='?', help='Base protocol')
    parser.add_argument('-p2', '--proto2', dest='proto2', nargs='+', help='Versus protocols')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-s', '--seed-set', dest='seed_set', nargs='+', type=str,  help='Seed set')
    parser.add_argument('-o', '--out', dest='out', nargs='?', type=str, help='Out filename', default='out')
    parser.add_argument('-i', '--info', dest='info', choices=['report_pdr', 'event_pdr'], default='report_pdr', help='What info to use')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    data = {i: [] for i in [args.proto1] + args.proto2}


    for seed in args.seed_set:
        for proto in [args.proto1] + args.proto2:
            filename = args.filename.replace('$2', seed).replace('$1', proto)
            logger.debug('Base filename: ' + str(filename))

            stream = open(filename, 'r')
            loader = yaml.safe_load(stream)

            data[proto].append(np.average([ i[args.info] for i in loader['pdr'] if args.info in i]))


    fig, axs = plt.subplots(nrows=len(args.proto2), ncols=1, layout='compressed', figsize=(4, 12))
    for proto, ax in zip(args.proto2, axs.ravel()):
        ax.plot(data[args.proto1],data[proto],'o')
        ax.plot([0, 1], [0, 1], 'k-', alpha=0.75, zorder=0)
        ax.set_aspect('equal')
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.set_title(proto)
    plt.show()
    fig.savefig(args.out+'.pdf', bbox_inches='tight')

