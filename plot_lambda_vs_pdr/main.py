#!/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse as ap
import sys
import logging
logger = logging.getLogger(__name__)

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 14

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog='plot_lambda_vs_pdr', description='Plot average pdr against lambda',
                                     epilog=':-(')
    parser.add_argument('-f', '--file', dest='file', type=str, help='Template file, $3 is seed $1 is protocol $2 is lambda')
    parser.add_argument('-s', '--seed', dest='seed', type=int, help='Seeds', nargs='*')
    parser.add_argument('-p', '--proto', dest='proto', type=str, help='protocols', nargs='*')
    parser.add_argument('-l', '--lambda', dest='lambda_p', type=str, help='Lambda parameter', nargs='*')
    parser.add_argument('-la', '--labels', dest='labels', type=str, help='Labels', nargs='*')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    raw_results = { i:{j:[] for j in args.lambda_p} for i in args.proto }
    for proto in args.proto:
        for lmbd in args.lambda_p:
            for seed in args.seed:
                filename = args.file.replace('$3', str(seed)).replace('$1', proto).replace('$2', str(lmbd))
                try:
                    raw_results[proto][lmbd].append(pd.read_pickle(filename))
                except:
                    logger.error(f'File {filename} not found')

    results = { i:{j:[] for j in args.lambda_p} for i in args.proto }
    for proto in args.proto:
        results[proto]= {j: np.average(raw_results[proto][j]) for j in args.lambda_p}

    fig,axs = plt.subplots(nrows=1, ncols=1,constrained_layout=True)
    x_axis = [float(i) for i in args.lambda_p]
    for proto in args.proto:
        axs.plot(args.lambda_p, results[proto].values())
    if args.labels:
        axs.legend(args.labels, loc='center left')
    axs.set_xlabel(r'$\lambda$ parameter')
    axs.set_ylabel('PDR')
    axs.grid(True)
    axs.set_xlim([min(axs.get_xticks()), max(axs.get_xticks())])
    plt.savefig('lambda_vs_pdr.pdf')