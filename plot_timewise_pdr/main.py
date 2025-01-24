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

def get_border_nodes(nw_yml):
    return [ i['node'] for i in nw_yml if 'border' in [j['role'] for j in i['engines']]]

def calculate_chebyshev(arr):
    return np.sum(np.power(arr, 2))**2/ ( len(arr)* np.sum(np.power(arr, 4)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_timewise_pdr', description='Plot MsR2MRP related PDR data', epilog=':-(')
    parser.add_argument('-e', '--energy', dest='nrg_file', action='store', help='The energy file', required=True, nargs='+')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--image', dest='image', action='store_true', default=False, help='Save as image')
    parser.add_argument('-o', '--output', dest='output', action='store', help='Output file', default='plot')
    parser.add_argument('-s', '--source', dest='source', choices=['e_pdr','r_pdr'], default='r_pdr', help='Packet type')
    parser.add_argument('-l', '--legend', dest='legend', action='store', nargs='+')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    match args.source:
        case 'r_pdr':
            s_sel = 'report_'
        case 'e_pdr':
            s_sel = 'event_'

    fig, axs = plt.subplots(nrows=len(args.nrg_file)+1, ncols=1, layout='compressed', figsize=(8,16), gridspec_kw={'height_ratios': [1, 4]})
    axs_arr = axs.ravel()
    for idx, n_f in enumerate(args.nrg_file):
        stream = open(n_f, 'r')
        nrg_yml = yaml.safe_load(stream)

        chebyshev_arr = []
        node_nrg_arr = []

        ts = [i['timestamp'] for i in nrg_yml['nrg_list']]

        values = pd.DataFrame()
        colors = pd.DataFrame()
        alpha = pd.DataFrame()

        recv_arr = [[j[s_sel+'recv'] for j in i['nodes']] for i in nrg_yml['nrg_list']]
        sent_arr = [[j[s_sel+'sent'] for j in i['nodes']] for i in nrg_yml['nrg_list']]
        res_recv_arr = [ np.array(d)-np.array(c) for c, d in zip(recv_arr[:-1], recv_arr[1:])]
        res_sent_arr = [np.array(d) - np.array(c) for c, d in zip(sent_arr[:-1], sent_arr[1:])]
        res_arr = [i/j for i,j in zip(res_recv_arr, res_sent_arr)]

        for i_idx,i in enumerate(nrg_yml['nrg_list'][:-1]):
            b_nrg_arr = [ n['energy'] for n in i['nodes'] if n['role'] == 'border']
            chebyshev_arr.append(calculate_chebyshev(b_nrg_arr))
            values[i['timestamp']] = res_arr[i_idx]
            role_arr = [n['role'] for n in  i['nodes']]
            colors[i['timestamp']] = [ 'blue' if i == 'border' else 'grey' for i in role_arr ]
            alpha[i['timestamp']] = [ 1.0 if i == 'border' else 0.5 for i in role_arr ]

        axs_arr[0].plot(chebyshev_arr)
        if args.legend:
            axs_arr[0].legend(args.legend)
        #else:
        #    axs_arr[0].legend(args.nrg_file)


        for index, row in values.iterrows():
            xy = list(map(list, zip(row.index,row.values,colors.loc[index].values,alpha.loc[index].values)))
            for start, stop in zip(xy[:-1], xy[1:]):
                x, y, z, v = zip(start, stop)
                axs_arr[idx+1].plot(x, np.array(y)+index, color=z[1],alpha=v[1])
    if args.image:
        fig.savefig(str(args.output)+'.pdf', bbox_inches='tight')
    else:
        plt.show()
