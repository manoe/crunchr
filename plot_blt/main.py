#!/bin/env python3

import argparse
import logging
import matplotlib
import pandas as pd

logger = logging.getLogger(__name__)
import sys
import matplotlib.pyplot as plt
import numpy as np
import yaml

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']


def calculate_chebyshev(arr):
    return np.sum(np.power(arr, 2))**2/ ( len(arr)* np.sum(np.power(arr, 4)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_blt', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('-p', '--pickle', dest='pickle_file', action='store', help='The pickle file', required=True, nargs='+')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--image', dest='image', action='store_true', default=False, help='Save as image')
    parser.add_argument('-o', '--output', dest='output', action='store', help='Output file', default='plot')
    parser.add_argument('-c', '--categories', dest='categories', action='store', nargs='+', help='Categories')
    parser.add_argument('-s', '--source', dest='source', action='store', choices=['lt','blt'], default='lt', help='Labels')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    fig, axs = plt.subplots(nrows=len(args.categories), ncols=1, layout='compressed',figsize=(8,8))
    axs_arr = axs.ravel()

    lts ={ i: {j : [] for j in args.categories} for i in ['lt', 'blt']}

    for idx, n_f in enumerate(args.pickle_file):
        data = pd.read_pickle(n_f)
        logger.debug('filename: '+str(n_f))
        for i in data.columns:
            if not np.isnan(data[i][0]):
                for j in args.categories:
                    if j in n_f:
                        lts[i][j].append(data[i][0])
                        logger.debug('Data stored: '+str(data[i][0]))
    all_values = [ min(i) for i in lts[args.source].values() ]
    min_bin = min(all_values)
    max_bin = max(all_values)
    logger.debug('min_bin: '+str(min_bin))
    logger.debug('max_bin: '+str(max_bin))
    min_count = []
    max_count = []
    for idx, data in enumerate(lts[args.source].items()):
        counts, bins = np.histogram(data[1],bins=20, range=(min_bin, max_bin))
        axs_arr[idx].hist(bins[:-1], weights=counts)
        axs_arr[idx].set_title(data[0])
        min_count.append(min(counts))
        max_count.append(max(counts))
    for i in axs_arr:
        i.set_xlim([min_bin, max_bin])
        i.set_ylim([min(min_count), max(max_count)])
    if args.image:
        fig.savefig(str(args.output)+'.pdf', bbox_inches='tight')
    else:
        plt.show()
