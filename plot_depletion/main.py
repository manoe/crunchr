#!/bin/python3

import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_depletion', description='Plot node depletion over time', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    if args.filename == '-':
        stream = sys.stdin
    else:
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)
