#!/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse
import logging
from matplotlib.colors import TABLEAU_COLORS
from matplotlib.ticker import FuncFormatter
logger = logging.getLogger(__name__)

from matplotlib import rcParams

rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 12
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='model_vs_reach', description='Process ff related data', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename',
                        help='Filename, use $0, $1 , $2 for param 1, param 2, and $3, for seed, respectively.')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Log level')
    parser.add_argument('-p', '--proto', dest='proto', type=str, help='Protocols, $0', nargs='+')
    parser.add_argument('-p1', '--param-1', dest='param1', type=str, help='Parameter 1, $1', nargs='+')
    parser.add_argument('-l', '--labels', dest='labels', type=str, help='Labels for param 1', nargs='*')
    parser.add_argument('-p2', '--param-2', dest='param2', type=str, help='Parameter 2, $2', nargs='+')
    parser.add_argument('-s', '--seeds', dest='seeds', type=str, help='Seeds, $3', nargs='+')
    parser.add_argument('-o', '--out', dest='out_file', type=str, help='Out file', default='out')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    res = {p + '_' + p1 + '_' + p2: {'r': [], 'l': [], 'd': []} for p in args.proto for p1 in args.param1 for p2 in
           args.param2}

    for p in args.proto:
        for p1 in args.param1:
            for p2 in args.param2:
                filename = args.filename.replace('$0', p).replace('$1', p1).replace('$2', p2)
                logger.debug('Init filename: ' + str(filename))
                tables = {i: pd.DataFrame() for i in 'rld'}
                for s in args.seeds:
                    data = pd.read_pickle(filename.replace('$3', s))
                    logger.debug('seed: ' + str(s))
                    for d in data.columns:
                        tables[d][s] = data[d].values
                        timestamps = data[d].index.values
                for i in 'rld':
                    #res[p + '_' + p1 + '_' + p2][i].append(tables[i].mean(axis=1))
                    res[p + '_' + p1 + '_' + p2][i]=tables[i].mean(axis=1)

    if args.labels:
        if len(args.labels) != len(res.keys()):
            logger.error('Number of labels does not match product number of parameters')
            exit(1)

    fig, ax = plt.subplots(nrows=1, ncols=1, layout='compressed')
    for k, color in zip(res.keys(), TABLEAU_COLORS):
        ax.plot(timestamps, res[k]['r'], color=color)
        for d,l in zip(['l','d'], [':','--']):
            ax.plot(timestamps, res[k][d], color=color, ls=l)
        #for d, l in zip(['r', 'l', 'd'], ['-', ':', '--']):
        #    ax.plot(timestamps, res[k][d], color=color, ls=l)
#    for t, color in zip([args.proto[0]], list(TABLEAU_COLORS.keys())[len(res.keys()):]):
#        for d,l in zip(['l','d'], [':','--']):
#            ax.plot(timestamps, res[t][d], color=color, ls=l)

    if args.labels:
        labels=args.labels
    else:
        labels=list(res.keys())
    ax.legend(labels, loc='lower left', bbox_to_anchor=(0, 0.1))
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Node number')
    #ax.set_xticklabels([i for i in ax.get_xticklabels()])
    ax.set_xlim([0, max(timestamps)])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: '{0:.0f}'.format(x/60)))
    ax.grid(True)
    plt.savefig(args.out_file + '.pdf', dpi=300)