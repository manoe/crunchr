#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import sys
import networkx as nx

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_traffic', description='Plot traffic', epilog=':-(')
    parser.add_argument('-d', '--data',
                        action='store_true', dest='data')
    parser.add_argument('-s', '--save-image',
                        action='store_true', dest='save_image')
    parser.add_argument('filename', help='use ``-\'\' for stdin')
    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    ts = [i['timestamp'] for i in loader]
    recv_pkt = {i['node']: [0] for i in loader[0]['pdr']}
    sent_pkt = {i['node']: [0] for i in loader[0]['pdr']}

    for i in loader:
        for j in i['pdr']:
            sent_pkt[j['node']].append(j['sent'])
            recv_pkt[j['node']].append(j['recv'])

    for i in sent_pkt:
        sent_pkt[i] = list(np.subtract(sent_pkt[i][1:], sent_pkt[i][:-1]))
    for i in recv_pkt:
        recv_pkt[i] = list(np.subtract(recv_pkt[i][1:], recv_pkt[i][:-1]))

    pdr = {i: list(np.divide(recv_pkt[i], sent_pkt[i])) for i in recv_pkt}

    pdr_arr = list(np.nan_to_num(list(pdr.values())))

    plt.subplot(211)
    plt.plot(ts, sp.stats.entropy(pdr_arr, base=2))
    plt.ylim((5, 6))
    plt.subplot(212)
    plt.plot(ts, np.average(pdr_arr, axis=0))
    plt.ylim((0, 1))
    plt.fill_between(ts, np.add(np.average(pdr_arr, axis=0), np.std(pdr_arr, axis=0)),
                     np.subtract(np.average(pdr_arr, axis=0), np.std(pdr_arr, axis=0)), alpha=0.2)

    plt.tight_layout()
    if args.save_image:
        plt.savefig(args.filename.replace('yaml', 'png'), bbox_inches='tight', )
    else:
        plt.show()
