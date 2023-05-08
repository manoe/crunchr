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

    if_arr = []
    for i in loader['loc_pdr']:
        if_arr.append(i['pong_table'])

    print(len(if_arr))

