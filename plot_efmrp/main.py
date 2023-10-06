#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx
import matplotlib



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_efmrp', description='Plot EFMRP network', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    graph = nx.DiGraph()

    for i in loader['loc_pdr']:
        print(i)