#!/bin/env python3

import argparse
import logging
import matplotlib
import pandas as pd
from matplotlib.lines import lineStyles
from matplotlib.lines import Line2D

import matplotlib.patches as mpatches
logger = logging.getLogger(__name__)
import sys
import matplotlib.pyplot as plt
import numpy as np
import yaml

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
#rcParams["text.usetex"] = True


def get_border_nodes(nw_yml):
    return [ i['node'] for i in nw_yml if 'border' in [j['role'] for j in i['engines']]]

def calculate_chebyshev(arr):
    return np.sum(np.power(arr, 1))**2/ ( len(arr)* np.sum(np.power(arr, 2)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_chebyshev_curve', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('-e', '--energy', dest='nrg_file', action='store', help='The energy file', required=True, nargs='+')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--image', dest='image', action='store_true', default=False, help='Save as image')
    parser.add_argument('-o', '--output', dest='output', action='store', help='Output file', default='plot')
    parser.add_argument('-s', '--source', dest='source', choices=['l_energy','c_energy', 'pkt'], default='l_energy', help='Data source')
    parser.add_argument('-l', '--legend', dest='legend', action='store', nargs='+')
    parser.add_argument('-t', '--to', dest='to', action='store', type=int)
    parser.add_argument('-p', '--period', dest='period', action='store', type=int, default=30)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    match args.source:
        case 'c_energy':
            s_sel = 'consumed_energy'
        case 'l_energy':
            s_sel = 'energy'
        case 'pkt':
            s_sel = 'pkt_forw'
    title = ['(' + i + ')' for i in 'abcdefg']
    fig, axs = plt.subplots(nrows=len(args.nrg_file)+1, ncols=1, layout='compressed', figsize=(8,12))
    axs_arr = axs.ravel()
    ax2 = axs_arr[0].twinx()
    ax2.set_ylabel('Dead node (count)')

    for idx, n_f in enumerate(args.nrg_file):
        stream = open(n_f, 'r')
        nrg_yml = yaml.safe_load(stream)
        if args.to:
            nrg_yml['nrg_list'] = nrg_yml['nrg_list'][:args.to]

        chebyshev_arr = []
        node_nrg_arr = []
        dead_node_arr = []

        ts = [i['timestamp'] for i in nrg_yml['nrg_list']]

        values = pd.DataFrame()
        colors = pd.DataFrame()
        alpha = pd.DataFrame()
        styles = pd.DataFrame()

        for i in nrg_yml['nrg_list']:
            b_nrg_arr = [ n[s_sel] for n in i['nodes'] if n['role'] == 'border' and n[s_sel] > 0]
            dead_node_arr.append(len( [n for n in i['nodes'] if n['role'] == 'border' and n[s_sel] == 0]))
            chebyshev_arr.append(calculate_chebyshev(b_nrg_arr))
            tmp_values = [n[s_sel] for n in  i['nodes'] if n['role'] != 'central']
            tmp_values.append(np.average(b_nrg_arr))
            values[i['timestamp']] = tmp_values
            role_arr = [n['role'] for n in  i['nodes'] if n['role'] != 'central']
            role_arr.append('avg_border')
            colors[i['timestamp']] = [ 'blue' if i == 'border' else 'red' if i == 'avg_border' else 'grey' for i in role_arr ]
            styles[i['timestamp']] = [ 'dotted' if i == 'avg_border' else 'solid' for i in role_arr ]
            alpha[i['timestamp']] = [ 1.0 if i == 'border' else  1 if i == 'avg_border' else 0.25 for i in role_arr ]

        axs_arr[0].plot(ts,chebyshev_arr)
        ax2.plot(ts,dead_node_arr, linestyle='dotted')

        if args.legend:
            axs_arr[0].legend(args.legend)
        else:
            axs_arr[0].legend(args.nrg_file)


        for index, row in values.iterrows():
            xy = list(map(list, zip(row.index,row.values,colors.loc[index].values,alpha.loc[index].values, styles.loc[index].values)))
            for start, stop in zip(xy[:-1], xy[1:]):
                x, y, z, v, w = zip(start, stop)
                axs_arr[idx+1].plot(x, y, color=z[1],alpha=v[1], linestyle=w[1])

    for idx,axs in enumerate(axs_arr):
        axs.set_title(title[idx], loc='left', pad=5, x=-0.07)
        axs.set_xlabel('Time (m)')
        if idx != 0:
            axs.set_ylabel('Energy (J)')
        else:
            axs.set_ylabel(r'Energy balance ($\Phi$)')
        axs.margins(0.0, 0.02)
        axs.set_yticklabels(["{:0.2f}".format(i) for i in axs.get_yticks()])
        axs.set_xticklabels(["{:0.0f}".format(i/60) for i in axs.get_xticks()])
        for i in range(len(ts)+1):
            if i*args.period % 3600 == 0:
                axs.axvline(x=i, color = 'grey', linestyle = 'dotted', alpha=0.5)

    colors = ['red', 'blue', 'grey']
    styles = ['dotted', 'solid', 'solid']
    lines = [Line2D([0], [0], color=c, linewidth=3, linestyle=s) for c,s in zip(colors,styles)]
    labels = ['Border node average', 'Border node', 'Sensor node']
    axs_arr[-1].legend(lines, labels)

    if args.image:
        fig.savefig(str(args.output)+'.pdf', bbox_inches='tight')
    else:
        plt.show()
