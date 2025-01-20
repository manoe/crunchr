#!/bin/env python3

import argparse
import logging
import matplotlib

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
    parser = argparse.ArgumentParser(prog='plot_chebyshev_curve', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('-n', '--network' ,dest='nw_file',action='store', help='The network file', required=True)
    parser.add_argument('-e', '--energy', dest='nrg_file', action='store', help='The energy file', required=True, nargs='+')
    parser.add_argument('-b', '--border', dest='border', action='store', help='Mark border node', type=int)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-i', '--image', dest='image', action='store_true', default=False, help='Save as image')
    parser.add_argument('-l', '--legend', dest='legend', action='store_true', default=False, help='Show legend')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    logger.debug('Network filename: ' + str(args.nw_file))

    stream = open(args.nw_file, 'r')
    nw_yml = yaml.safe_load(stream)

    borders = get_border_nodes(nw_yml)
    fig, axs = plt.subplots(nrows=len(args.nrg_file)+1, ncols=1, layout='compressed')
    for idx, n_f in enumerate(args.nrg_file):
        stream = open(n_f, 'r')
        nrg_yml = yaml.safe_load(stream)

        chebyshev_arr = []
        node_nrg_arr = { n: [] for n in borders }

        for i in nrg_yml['nrg_list']:
            nrg_arr = []
            for k in i['nodes']:
                if k['node'] in borders:
                    nrg_arr.append(k['consumed_energy'])
                    node_nrg_arr[k['node']].append(k['consumed_energy'])
            logger.debug('nrg arr: '+str(nrg_arr))
            chebyshev_arr.append(calculate_chebyshev(nrg_arr))

        axs.ravel()[0].plot(chebyshev_arr)

        for i in node_nrg_arr:
            if args.border and i == args.border:
                axs.ravel()[idx + 1].plot(node_nrg_arr[i], linestyle=':')
            else:
                axs.ravel()[idx + 1].plot(node_nrg_arr[i])
        if args.legend:
            axs.ravel()[idx + 1].legend(node_nrg_arr.keys())

    if args.image:
        fig.savefig('plot.pdf', bbox_inches='tight')
    else:
        plt.show()
