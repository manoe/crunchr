#!/bin/env python3
import numpy as np
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
    parser.add_argument('-l', '--lower-than', dest='lower', type=float, help='Link PDR lower than')
    parser.add_argument('-g', '--greater-than', dest='greater', type=float, help='Link PDR greater than')
    parser.add_argument('-hst','--histogram', dest='histogram', action='store_true', default=False, help='Show histogram')
    parser.add_argument('-q', '--qos', dest='qos', type=float, default=0.6, help='QoS')
    args = parser.parse_args()

#    nrows = math.ceil(len(args.filenames) / args.columns)
#    ncols = args.columns
    nrows = 1
    ncols = 1
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols)

    if args.histogram:
        print(args.filenames[0])
        data = pd.read_pickle(args.filenames[0])
        bins=np.arange(start=0.1,stop=1.1,step=0.1)
        p_arr = [ entry['meas_t'] for entry in data]
        counts, bins = np.histogram(p_arr,bins=bins)

        bin_tup = list(zip(bins, bins[1:]))

        counts_cond = []
        for bin in bin_tup:
            counts_cond.append(len([i for i in data if bin[0] < i['meas_t'] < bin[1] and i['meas_q'] > args.qos]) / (len(data)))

        counts = [ i/sum(counts) for i in counts]

        for idx,i in enumerate(bins):
            print(i)
            print(np.inner(counts[:idx],counts_cond[:idx]))
            print(np.sum(counts_cond[:idx]))
            #print(' P(p\'>c| p=i/n) P(=i/n)')



        ax.stairs(counts, bins)
        plt.tight_layout()
        plt.show()
        exit(0)

    for filename in args.filenames:
        print(filename)
        data = pd.read_pickle(filename)
        if 'lower' in args:
            print('Lower ratio: '+str(len([i for i in data if i['meas_t'] < args.lower])/len(data)))
        if 'greater' in args:
            print('Higher ratio: '+str(len([i for i in data if i['meas_t'] > args.greater]) / len(data)))