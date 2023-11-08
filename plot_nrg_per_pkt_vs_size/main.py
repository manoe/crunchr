#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_nrg_per_pkt_vs_size', description='Plot energy per received packet vs network size', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-c', '--count', action='store', dest='count', default=10, type=int)
    parser.add_argument('-p', '--percent', action='store', dest='percent', default='0.8',
                        help='Init percentage', type=float)
    parser.add_argument('-s', '--size', action='store', dest='size', help='network size, n x n', nargs='+', type=int)
    parser.add_argument('-d', '--data', action='store_true', dest='data')
    parser.add_argument('-e', '--errorbar', action='store_true')

    parser.add_argument('filename', help='filename prefixes', nargs='+')

    args = parser.parse_args()

    args.size.sort()

    files = args.filename

    y_nrg = {}
    y_nrg_std = {}
    y_time = {}
    y_time_std = {}

    for filename in files:
        y_nrg[filename] = {}
        y_nrg_std[filename] = {}

        for s in args.size:
            stream = open(filename+'_'+str(s)+'.yaml', 'r')
            node = s**2-1

            print('Processing '+filename+' with size '+str(s))

            loader = yaml.safe_load(stream)

            pkt_list = {}
            fail = 0

            data = [j['pkt_list'][-1]['energy']/len(j['pkt_list']) for j in loader['runs']]

            y_nrg[filename][s] = np.average(data)
            y_nrg_std[filename][s] = np.std(data)

    width = 0.8
    bar_width = width / len(y_nrg)

    idx = 0
    if args.errorbar:
        for idx, data in enumerate(y_nrg):
            plt.errorbar([x + idx*bar_width-width/2 for x in range(len(args.size))], list(y_nrg[data].values()),
                         list(y_nrg_std[data].values()), linestyle='None')
    else:
        for idx, i in enumerate(y_nrg):
            bc = plt.bar([x + idx*bar_width-width/2 for x in range(len(args.size))] , y_nrg[i].values(), bar_width)
            plt.bar_label(bc, label=args.size)
            idx += 1

    plt.title('Consumed energy per packet vs. size')
    plt.xticks(range(len(args.size)), labels=args.size)

    plt.legend(y_time.keys())
    plt.show()
    exit(0)
