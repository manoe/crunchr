#!/bin/env python3

import argparse
import logging
import matplotlib
import pandas as pd

logger = logging.getLogger(__name__)
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import yaml

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 15.0


def calculate_chebyshev(arr):
    return np.sum(np.power(arr, 2))**2/ ( len(arr)* np.sum(np.power(arr, 4)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_blt', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('-p', '--pickle', dest='pickle_file', action='store', help='The pickle file', required=True, nargs='+')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--image', dest='image', action='store_true', default=False, help='Save as image')
    parser.add_argument('-o', '--output', dest='output', action='store', help='Output file', default='plot')
    parser.add_argument('-c', '--categories', dest='categories', action='store', nargs='+', help='Categories')
    parser.add_argument('-s', '--source', dest='source', action='store', choices=['lt','blt','both'], default='lt', help='Labels')
    parser.add_argument('-f', '--cdf', dest='cdf', action='store_true', default='false', help='Plot cdf')
    args = parser.parse_args()

    title = [ '('+i+')' for i in 'abcdefg']

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

    if args.source == 'both':
        all_min_values = [min(i) for j in lts.keys() for i in lts[j].values() ]
        all_max_values = [max(i) for j in lts.keys() for i in lts[j].values()]
        min_bin = min(all_min_values)
        max_bin = max(all_max_values)
        logger.debug('min_bin: ' + str(min_bin))
        logger.debug('max_bin: ' + str(max_bin))
        min_count = []
        max_count = []
        for source in ['lt', 'blt']:
            for idx, data in enumerate(lts[source].items()):
                counts, bins = np.histogram(data[1], bins=20, range=(min_bin, max_bin))
                logger.debug('bins: ' + str(bins))
                logger.debug('counts: ' + str(counts))
                if source == 'lt':
                    corr = (bins[1]-bins[0])/8.0
                    color = 'tab:orange'
                else:
                    corr = -(bins[1]-bins[0])/8.0
                    color = 'tab:blue'
                if args.cdf:
                    # counts = np.cumsum(counts)
                    axs_arr[idx].hist(bins[:-1], bins+corr, weights=counts, rwidth=0.6, cumulative=True, density=True,color=color)
                else:
                    axs_arr[idx].hist(bins[:-1], bins, weights=counts, rwidth=0.4, alpha=0.5)
                # axs_arr[idx].set_title(data[0])
                axs_arr[idx].set_title(title[idx], loc='left', pad=10, x=-0.12)
                axs_arr[idx].set_xlabel('Time (min)')

                axs_arr[idx].set_ylabel('First node failure \n (probability)')
                min_count.append(min(counts))
                max_count.append(max(counts))

            for idx, i in enumerate(axs_arr):
                i.set_xlim([min_bin, max_bin])
                if not args.cdf:
                    i.set_ylim([min(min_count), max(max_count) * 1.1])

                # ticks = [ (i[1]-i[0])/2.0+i[0] for i in zip(bins[:-1], bins[1:])]
                ticks = bins
                i.set_xticks(ticks)
                tick_labels = ["{:.0f}".format(i / 60) for i in ticks]
                i.set_xticklabels(tick_labels)


                # i.set_xlabel()
        red_patch = mpatches.Patch(color='tab:blue', label='Border node')
        blue_patch = mpatches.Patch(color='tab:orange', label='Every node')
        axs_arr[-1].legend(loc='best',handles=[red_patch, blue_patch])

    else:
        all_min_values = [ min(i) for i in lts[args.source].values() ]
        all_max_values = [ max(i) for i in lts[args.source].values() ]
        min_bin = min(all_min_values)
        max_bin = max(all_max_values)
        logger.debug('min_bin: '+str(min_bin))
        logger.debug('max_bin: '+str(max_bin))
        min_count = []
        max_count = []
        for idx, data in enumerate(lts[args.source].items()):
            counts, bins = np.histogram(data[1],bins=20, range=(min_bin, max_bin))
            logger.debug('bins: '+str(bins))
            logger.debug('counts: ' + str(counts))
            if args.cdf:
                #counts = np.cumsum(counts)
                axs_arr[idx].hist(bins[:-1], bins, weights=counts, rwidth=0.9, cumulative=True, density=True)
            else:
                axs_arr[idx].hist(bins[:-1], bins, weights=counts, rwidth=0.9)
            #axs_arr[idx].set_title(data[0])
            axs_arr[idx].set_title(title[idx], loc='left', pad=5, x=-0.065)
            axs_arr[idx].set_xlabel('Time (min)')
            if args.source == 'lt':
                axs_arr[idx].set_ylabel('First node failure (probability)')
            else:
                axs_arr[idx].set_ylabel('First border node failure (probability)')
            min_count.append(min(counts))
            max_count.append(max(counts))
        for idx,i in enumerate(axs_arr):
            i.set_xlim([min_bin, max_bin])
            if not args.cdf:
                i.set_ylim([min(min_count), max(max_count)*1.1])


            #ticks = [ (i[1]-i[0])/2.0+i[0] for i in zip(bins[:-1], bins[1:])]
            ticks = bins
            i.set_xticks(ticks)
            tick_labels = ["{:.0f}".format(i/60) for i in ticks]
            i.set_xticklabels(tick_labels)
            #i.set_xlabel()
    if args.image:
        fig.savefig(str(args.output)+'.pdf', bbox_inches='tight')
    else:
        plt.show()
