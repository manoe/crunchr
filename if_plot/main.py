#!/bin/env python3

import yaml
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='if_plot', description='Plot interference related graphs', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    if_arr = [i['pong_table'] for run in loader['runs'] for i in run['loc_pdr']]
    bins = np.arange(np.min(if_arr), np.max(if_arr), 1)

    plt.subplot(211)
    plt.hist(if_arr, bins)
    plt.subplot(212)

    log_if_arr = [ np.log10(i) for i in if_arr ]
    plt.hist(log_if_arr, np.arange(np.min(log_if_arr), np.max(log_if_arr), 0.05))

    plt.show()
    plt.tight_layout()

