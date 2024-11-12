#!/bin/env python3

import yaml
import matplotlib.pyplot as plt
import argparse
import sys
import math
import numpy as np
from numpy.ma.core import ravel, arange
import pandas as pd


def get_borders(top):
    if 'runs' in top:
        data = top['runs'][0]['loc_pdr']
    else:
        data = top
    borders = []
    for i in data:
        for j in i['engines']:
            if j['role'] == 'border' and len(j['hop_pkt_table']) > 0:
                borders.append({'node': i['node'], 'hop_pkt_table': j['hop_pkt_table']})
    return borders


def get_hop_pkt_list(borders):
    x_bars = []
    for b_idx, border in enumerate(borders):
        x = [ i['hop'] for i in border['hop_pkt_table']]
        bars = [i['pkt_count'] for i in border['hop_pkt_table']]
        x_bars.append( {'node': border['node'], 'list': dict(zip(x, bars))})
    return x_bars


def get_hop_pkt_stat(x_bars):
    max_hop = max([max(i['list'].keys()) for i in x_bars])
    table = pd.DataFrame(index=list(range(1, max_hop + 1)), columns=list(range(1, len(x_bars) + 1)))

    for b_idx,b in enumerate(x_bars):
        for i in b['list'].keys():
            table.at[i,b_idx] = b['list'][i]
    table.fillna(0)
    return table


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='border_plot', description='Plot MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin', nargs='*')
    parser.add_argument('-c', '--columns', dest='columns', type=int, default=2, help='Number of columns in plot')
    args = parser.parse_args()

    if len(args.filename) > 1:
        means = []
        for filename in args.filename:
            stream = open(filename, 'r')
            loader = yaml.safe_load(stream)
            borders = get_borders(loader)
            hop_pkt_list = get_hop_pkt_list(borders)
            table = get_hop_pkt_stat(hop_pkt_list)
            means.append({'hop': table.index, 'mean': table.mean(axis=1)})
        print(means)
        max_hop = max([max(i['hop']) for i in means])
        table = pd.DataFrame(index=list(range(1, max_hop + 1)), columns=range(len(means)))
        for m_idx, m in enumerate(means):
            for idx,i in enumerate(m['hop']):
                table.at[i, m_idx] = m['mean'][i]
        table.fillna(0)
        fig, ax = plt.subplots(1, 1)
        print(table) # .std(axis=1)
        ax.bar(table.index, table.mean(axis=1), yerr=table.std(axis=1), align='center', ecolor='black', capsize=10)
#        ax.errorbar(table.index, table.mean(axis=1), table.std(axis=1), fmt='.', color='Black', elinewidth=2, capthick=10, errorevery=1, alpha=0.5, ms=4,
#                     capsize=2)
        ax.title.set_text('Average hop/pkt')
        plt.tight_layout()
        plt.show()
    else:
        stream = sys.stdin
        if args.filename[0] != '-':
            stream = open(args.filename[0], 'r')
        loader = yaml.safe_load(stream)
        borders = get_borders(loader)

        hop_pkt_list = get_hop_pkt_list(borders)
        nrows = math.ceil((len(hop_pkt_list) + 1) / 2)
        ncols = args.columns
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols)
        ax_arr = axs.ravel()

        for idx,i in enumerate(hop_pkt_list):
            ax_arr[idx].bar(i['list'].keys(), i['list'].values())
            ax_arr[idx].title.set_text('Node '+str(i['node']))
            ax_arr[idx].set_xticks(np.arange(len(i['list'].keys())+1))

        table = get_hop_pkt_stat(hop_pkt_list)

        ax_arr[len(borders)].bar(table.index, table.mean(axis=1))
        ax_arr[len(borders)].title.set_text('Average hop/pkt')

        plt.tight_layout()
        plt.show()
