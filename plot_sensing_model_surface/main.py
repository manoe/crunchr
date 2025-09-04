#!/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse
import logging
from matplotlib.colors import TABLEAU_COLORS
from matplotlib.ticker import FuncFormatter
logger = logging.getLogger(__name__)
from scipy.interpolate import interp1d, pchip
from scipy.signal import savgol_filter

from matplotlib import rcParams
from matplotlib import cm
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 12
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_sensing_model_surface', description='Process ff related data ', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename',
                        help='Filename, use $0, $1 , $2 for param 1, param 2, and $3, for seed, respectively.')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Log level')
    #parser.add_argument('-p', '--smod', dest='smod', type=str, help='Sensing model, $0', nargs='+')
    parser.add_argument('-p1', '--param-1', dest='param1', type=str, help='Parameter 1, $1', nargs='+')
    parser.add_argument('-l', '--labels', dest='labels', type=str, help='Labels for param 1', nargs='*')
#    parser.add_argument('-p2', '--param-2', dest='param2', type=str, help='Parameter 2, $2', nargs='+')
    parser.add_argument('-s', '--seeds', dest='seeds', type=str, help='Seeds, $3', nargs='+')
    parser.add_argument('-o', '--out', dest='out_file', type=str, help='Out file', default='out')
    parser.add_argument('-a', '--attribute', dest='attribute', type=str, help='Plot attribute', default='r', choices=['r', 'l', 'b', 'm', 'e'])
    parser.add_argument('-m', '--limit', dest='limit', type=int, help='Limit frame processing to nth frame')
    parser.add_argument('-e', '--extend', dest='extend', action='store_true', help='Extend series to match the longest series')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    res = {p1: {'r': [], 'l': [], 'd': [], 'm': []} for p1 in args.param1 }

    #for p in args.smod:
    for p1 in args.param1:
        #filename = args.filename.replace('$0', p).replace('$1', p1)
        filename = args.filename.replace('$1', p1)
        logger.debug('Init filename: ' + str(filename))
        tables = {i: pd.DataFrame() for i in 'rldme'}
        max_len = 0
        for s in args.seeds:
            data = pd.read_pickle(filename.replace('$3', s))
            logger.debug('seed: ' + str(s))
            for d in data.columns:
                if args.limit:
                    tables[d][s] = data[d].iloc[:args.limit].values
                    timestamps = data[d].iloc[:args.limit].index.values
                else:
                    #tables[d][s] = data[d].values
                    tables[d] = pd.concat([tables[d], pd.Series(data[d].values) ], axis=1)
                    if 'timestamps' not in locals() or len(timestamps) < len(data[d].index.values):
                        timestamps = data[d].index.values
                    if len(data[d].values) > max_len:
                        max_len = len(data[d].values)

        for i in 'rldme':
            #res[p + '_' + p1 + '_' + p2][i].append(tables[i].mean(axis=1))
            res[p1][i]=tables[i].mean(axis=1)

    for p1 in args.param1:
        for i in 'rldme':
            res[p1][i] = pd.concat([ res[p1][i], pd.Series([res[p1][i].iloc[-1] for j in range(len(res[p1][i]), max_len)])], ignore_index=True)

    logger.debug('Max len: ' + str(max_len))

    if args.labels:
        if len(args.labels) != len(res.keys()):
            logger.error('Number of labels does not match product number of parameters')
            exit(1)

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    #fig, ax = plt.subplots(nrows=1, ncols=1, layout='compressed')

    X = timestamps
    Y = [int(idx) for idx, i in enumerate(list(args.param1))]

    for idx, i in enumerate(args.param1):
        #yhat = savgol_filter(res[i][args.attribute], 2, 1)
        yhat = res[i][args.attribute]
        ax.plot(xs=X, ys=yhat, zs=idx, zdir='y', alpha=0.8)
        # ax.plot(xs=X, ys = res[i][args.attribute], zs=idx, zdir='y', alpha=0.8)
#    X, Y = np.meshgrid(X, Y)
#
#    Z = np.empty((len(X),len(Y[0])))
#
#    for idx, i in enumerate(args.param1):
#        Z[idx] = res[i][args.attribute]
#
#    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
#    fig.colorbar(surf, shrink=0.5, aspect=5)
#
#    ax.set_yticks([int(idx) for idx, i in enumerate(list(args.param1))])
#    ticklabels = ax.get_yticklabels()
#    ticklabels[len(ticklabels) - len(list(args.param1)):] = list(args.param1)
#
#    ax.set_yticklabels(ticklabels)

    ax.set_yticks(Y)
    ax.set_yticklabels(args.param1)
    ax.legend(args.param1)
    plt.savefig(args.out_file + '.pdf', dpi=300)
    plt.show()

#import matplotlib.pyplot as plt
#import numpy as np
#
#from matplotlib import cm
#from matplotlib.ticker import LinearLocator
#
#
#if __name__ == '__main__':
#    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
#
#    # Make data.
#    X = np.arange(-5, 5, 0.25)
#    Y = np.arange(-5, 5, 0.25)
#    X, Y = np.meshgrid(X, Y)
#    R = np.sqrt(X**2 + Y**2)
#    Z = np.arctan(R)
#
#    # Plot the surface.
#    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
#                           linewidth=0, antialiased=False)
#
#    # Customize the z axis.
#    ax.set_zlim(-1.01, 1.01)
#    ax.zaxis.set_major_locator(LinearLocator(10))
#    # A StrMethodFormatter is used automatically
#    ax.zaxis.set_major_formatter('{x:.02f}')
#
#    # Add a color bar which maps values to colors.
#    fig.colorbar(surf, shrink=0.5, aspect=5)
#
#    plt.show()