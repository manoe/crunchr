#!/bin/env python3

import argparse
from zipfile import sizeEndCentDir

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 12

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_sensor_reading', description='Plot sensor reading', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='Filename, $1 for variable, $2 for seed')
    parser.add_argument('-s', '--seed', dest='seed', help='Seeds', nargs='+')
    parser.add_argument('-l', '--label', dest='labels', help='Labels', nargs='+')
    parser.add_argument('-p', '--params', dest='params', nargs='+')
    args = parser.parse_args()

    arr = { i: pd.Series() for i in args.params }

    if 'labels' in args:
        labels = [i for i in args.labels]
    else:
        labels = [i for i in args.params]
    fig, ax = plt.subplots()

    for p_idx, p in enumerate(args.params):
        for s in args.seed:
            data = pd.read_pickle(args.filename.replace('$1',p).replace('$2',s))

            arr[p] = pd.concat([arr[p], data['sensor_value']], ignore_index=True)


        bins = np.arange(0,8.1,0.5)

        offset = [1, 2]
        counts, bins = np.histogram(arr[p][arr[p] > 0][arr[p] < 8], bins, density=True)
        ax.bar(bins[:-1]+offset[p_idx]*0.125+0.075, counts, width=0.25, alpha=0.5, label=labels[p_idx])
    ax.set_xlabel('Sensor reading value')
    ax.set_ylabel('Occurrence probability')
    ax.set_xticks(bins)
    ax.set_xticklabels(bins)
    ax.legend()
    fig.savefig('out.pdf', bbox_inches='tight')
