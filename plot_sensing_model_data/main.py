#!/bin/env python3
import math

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
import numpy as np
import scipy.stats as st
from matplotlib import rcParams
from matplotlib import cm
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 12
import sys

attr_arr = ['r', 'l', 'd', 'm', 'e', 'pr', 'pe']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_sensing_model_surface', description='Process ff related data ', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename',
                        help='Filename, use $0, $1 , $2 for param 1, param 2, and $3, for seed, respectively.')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Log level')
    parser.add_argument('-p', '--plot', dest='plot', type=str, help='Plot kind', default='graph', choices=['graph', 'bar'])
    parser.add_argument('-p1', '--param-1', dest='param1', type=str, help='Parameter 1, $1', nargs='+')
    parser.add_argument('-p2', '--param-2', dest='param2', type=str, help='Parameter 2, $2', nargs='+')
    parser.add_argument('-l', '--labels', dest='labels', type=str, help='Labels for param 1', nargs='*')
    #    parser.add_argument('-p2', '--param-2', dest='param2', type=str, help='Parameter 2, $2', nargs='+')
    parser.add_argument('-s', '--seeds', dest='seeds', type=str, help='Seeds, $3', nargs='+')
    parser.add_argument('-o', '--out', dest='out_file', type=str, help='Out file', default='out')
    parser.add_argument('-a', '--attribute', dest='attribute', type=str, help='Plot attribute', default=attr_arr[0], choices=attr_arr)
    parser.add_argument('-m', '--limit', dest='limit', type=int, help='Limit frame processing to nth frame')
    parser.add_argument('-e', '--extend', dest='extend', action='store_true', help='Extend series to match the longest series')
    parser.add_argument('-w', '--window', dest='window', action='store_true', help='Plot multiple windows (not implemented)')
    parser.add_argument('-std', '--standard-deviation', dest='std', action='store_true',
                        help='Calculate STD instead of mean')
    parser.add_argument('-conf', '--confidence-interval', dest='conf', action='store_true',
                        help='Calculate STD instead of mean')


    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    res = {p2: {p1: {'r': [], 'l': [], 'd': [], 'm': [], 'pr': [], 'pe': []} for p1 in args.param1 } for p2 in args.param2}
    res_std = {p2: {p1: {'r': [], 'l': [], 'd': [], 'm': [], 'pr': [], 'pe': []} for p1 in args.param1 } for p2 in args.param2}
    res_conf = {p2: {p1: {'r': [], 'l': [], 'd': [], 'm': [], 'pr': [], 'pe': []} for p1 in args.param1 } for p2 in args.param2}

    #for p in args.smod:
    for p2 in args.param2:
        for p1 in args.param1:
            #filename = args.filename.replace('$0', p).replace('$1', p1)
            filename = args.filename.replace('$1', p1).replace('$2', p2)
            logger.debug('Init filename: ' + str(filename))
            tables = {i: pd.DataFrame() for i in attr_arr}
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

            for i in attr_arr:
                #res[p + '_' + p1 + '_' + p2][i].append(tables[i].mean(axis=1))
                res_std[p2][p1][i] = tables[i].std(axis=1)
                res[p2][p1][i] = tables[i].mean(axis=1)
                logger.debug('calculating '+str(i)+' for '+str(p1))
                def conf_int_wo_na(x):
                    arr = [i for i in x if i != np.nan]
                    if len(arr) > 0 or not all( i == 0 for i in arr ):
                        return st.t.interval(0.95, len(x) - 1, loc=np.mean(x), scale=st.sem(x))
                    else:
                        return (0,0)


                res_conf[p2][p1][i] = tables[i].apply(lambda x: conf_int_wo_na(x), axis=1)
                #res_conf[p1][i] = tables[i].fillna(0).apply(lambda x: st.t.interval(0.95, len(x)-1, loc=np.mean(x), scale=st.sem(x)) , axis=1)



                #st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))

        for p1 in args.param1:
            for i in attr_arr:

                res[p2][p1][i] = pd.concat([ res[p2][p1][i], pd.Series([res[p2][p1][i].iloc[-1] for j in range(len(res[p2][p1][i]), max_len)])], ignore_index=True)

        logger.debug('Max len: ' + str(max_len))

    if args.labels:
        if len(args.labels) != len(res.keys()):
            logger.error('Number of labels does not match product number of parameters')
            exit(1)



    if args.plot == 'graph':
        nrows = math.ceil(len(args.param2) / 2)
        fig, ax = plt.subplots(nrows=nrows, ncols=2)
        ax_arr = ax.ravel()
        # fig, ax = plt.subplots(nrows=1, ncols=1, layout='compressed')

        X = timestamps
        #    Y = [int(idx) for idx, i in enumerate(list(args.param1))]

        handle_list = []
        for a_idx, a in enumerate(args.param2):
            ax_arr[a_idx].set_title(a)
            for idx, i in enumerate(args.param1):
                handle, = ax_arr[a_idx].plot(X, res[a][i][args.attribute], alpha=0.8)
                handle_list.append(handle)
                if args.std:
                    ax_arr[a_idx].fill_between(X, res[a][i][args.attribute] - res_std[a][i][args.attribute],
                                    res[a][i][args.attribute] + res_std[a][i][args.attribute], color='#888888', alpha=0.2)
                if args.conf:
                    ax[a_idx].fill_between(X, res_conf[a][i][args.attribute].map( lambda x: x[0] ).fillna(0),
                                    res_conf[a][i][args.attribute].map( lambda x: x[1] ).fillna(0), color='#888888', alpha=0.2)

                print('Std of ' + str(i) + ' std: ' + str(np.std(res_std[a][i][args.attribute])))
                print('Sum of 95% confidence: '+str((res_conf[a][i][args.attribute].map(lambda x: x[1] ) - res_conf[a][i][args.attribute].map( lambda x: x[0] )).sum()))
        ax_arr[a_idx].legend(handle_list, args.param1)
    if args.plot == 'bar':
        fig, ax = plt.subplots(nrows=len(args.param2), ncols=1)
        ax_arr = ax.ravel()
        for a_idx, a in enumerate(args.param2):
            ax_arr[a_idx].set_title(a)
            if args.std:
                b = ax_arr[a_idx].bar(args.param1, [np.std(res_std[a][i][args.attribute]) for i in args.param1])
            if args.conf:
                b= ax_arr[a_idx].bar(args.param1, [(res_conf[a][i][args.attribute].map(lambda x: x[1]) - res_conf[a][i][
                    args.attribute].map(lambda x: x[0])).sum() for i in args.param1])
            ax_arr[a_idx].bar_label(b)

    plt.savefig(args.out_file + '.pdf', dpi=300)
    plt.show()
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

 #   ax.set_yticks(Y)
 #   ax.set_yticklabels(args.param1)

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