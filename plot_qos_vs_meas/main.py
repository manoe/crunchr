#!/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)
import argparse
import math

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_qos_vs_meas',
                                     description='Plot ', epilog=':-(')
    parser.add_argument('filenames', help='Input filenames', nargs='*')
    parser.add_argument('-c', '--columns', dest='columns', type=int, default=2, help='Column number')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-l', '--lower-than', dest='lower', type=float, default=0.8, help='Link PDR lower than')
    parser.add_argument('-g', '--greater-than', dest='greater', type=float, default=0.8, help='Link PDR greater than')
    args = parser.parse_args()

    nrows = math.ceil(len(args.filename) / args.columns)
    ncols = args.columns

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols)
    ax_list = ax.ravel()
    pickle_list = [pd.read_pickle(filename) for filename in args.filenames]

    for filename in args.filenames:
        print(filename)
        data = pd.read_pickle(filename)
        if 'lower' in args:
            print('Lower ratio: '+str(len([i for i in data if i['meas_t'] < args.lower])/len(data)))
        if 'higher' in args:
            print('Higher ratio: ' + str(len([i for i in data if i['meas_t'] > args.lower]) / len(data)))
