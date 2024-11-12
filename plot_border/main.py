#!/bin/env python3

import yaml
import matplotlib.pyplot as plt
import argparse
import sys
import math
import numpy as np
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
    parser = argparse.ArgumentParser(prog='plot_border', description='Plot MSR2MRP border node related pickleized stats', epilog=':-(')
    parser.add_argument('filename', help='Pickle(s) to read', nargs='+')
    parser.add_argument('-c', '--columns', dest='columns', type=int, default=2, help='Number of columns in plot')
    parser.add_argument('-t', '--title', dest='title', type=str, default=['MSR2MRP'], help='Plot title(s)', nargs='+')
    parser.add_argument('-g', '--global-title', dest='g_title', type=str)
    args = parser.parse_args()

    if len(args.filename) != len(args.title) and len(args.title) != 1:
        print(len(args.title))
        print('Filename and title must be the same amount')
        exit(1)

    nrows = math.ceil(len(args.filename) / 2)
    ncols = args.columns
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols)
    ax_list = ax.ravel()

    pickle_list = [pd.read_pickle(filename) for filename in args.filename]

    for idx,table in enumerate(pickle_list):
        ax_list[idx].bar(table.index, table.mean(axis=1), yerr=table.std(axis=1), align='center', ecolor='black', capsize=10)
        ax_list[idx].title.set_text(args.title[idx]+' - average hop/pkt')
        ax_list[idx].set_ylim(bottom=0)

    max_x = max([max(table.index) for table in pickle_list])
    max_y = max([max(table.mean(axis=1)) for table in pickle_list])

    list(map(lambda x: x.set_xlim(right=max_x), ax_list))
    list(map(lambda x: x.set_ylim(top=max_y), ax_list))


    if len(args.filename) % 2 == 1:
        ax_list[-1].axis('off')

    if 'g_title' in args:
        fig.suptitle(args.g_title)
    plt.tight_layout()
    plt.show()
