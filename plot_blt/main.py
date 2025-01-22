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
    parser.add_argument('-e', '--energy', dest='nrg_file', action='store', help='The energy file', required=True, nargs='+')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--image', dest='image', action='store_true', default=False, help='Save as image')
    parser.add_argument('-o', '--output', dest='output', action='store', help='Output file', default='plot')
    parser.add_argument('-c', '--categories', dest='categories', action='store', nargs='+', help='Categories')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    fig, axs = plt.subplots(nrows=len(args.categories), ncols=1, layout='compressed',figsize=(16,8))
    axs_arr = axs.ravel()

    blt = {i : [] for i in args.categories}

    for idx, n_f in enumerate(args.nrg_file):
        stream = open(n_f, 'r')
        nrg_yml = yaml.safe_load(stream)
        logger.debug('filename: '+str(n_f))
        for i in nrg_yml['nrg_list']:
            b_nrg_arr = [ n['energy'] for n in i['nodes'] if n['role'] == 'border']
            if min(b_nrg_arr) == 0:
                res=i['timestamp']
                for j in args.categories:
                    if j in n_f:
                        blt[j].append(res)
                break

    for idx, data in enumerate(blt.items()):
        counts, bins = np.histogram(data[1])
        axs_arr[idx].hist(bins[:-1], bins, weights=counts)
        axs_arr[idx].set_title(data[0])

    if args.image:
        fig.savefig(str(args.output)+'.pdf', bbox_inches='tight')
    else:
        plt.show()
