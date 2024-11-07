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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='border_plot', description='Plot MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')
    parser.add_argument('-c', '--columns', dest='columns', type=int, default=2, help='Number of columns in plot')
    parser.add_argument('-b', '--batch', dest='batch', type=str, nargs='+')
    args = parser.parse_args()

    stream = sys.stdin

    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    borders = get_borders(loader)

    nrows = math.ceil((len(borders)+1)/2)
    ncols = args.columns
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols)

    ax_arr = axs.ravel()

    b_total = {}

    max_hop = max([i['hop'] for border in borders for i in border['hop_pkt_table'] ])

    table = pd.DataFrame(index=list(range(1,max_hop+1)), columns=list(range(1,len(borders)+1)))


    for b_idx, border in enumerate(borders):
        x = [ i['hop'] for i in border['hop_pkt_table']]
        bars = [i['pkt_count'] for i in border['hop_pkt_table']]
        ax_arr[b_idx].bar(x, bars)
        ax_arr[b_idx].title.set_text('Node '+str(border['node']))
        ax_arr[b_idx].set_xticks(np.arange(len(x)+1))

        for idx,i in enumerate(x):
            table.at[i,b_idx]= bars[idx]
    table.fillna(0)
    ax_arr[len(borders)].bar( table.index, table.mean(axis=1))
    ax_arr[len(borders)].title.set_text('Average hop/pkt')

    #if nrows%2 > 0:
    #    ax_arr[-1].axis('off')


    plt.tight_layout()
    plt.show()
