#!/bin/env python3

import argparse
import logging
logger = logging.getLogger(__name__)
import pandas as pd
import sys
import matplotlib.pyplot as plt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='msr2mrp_meas_1_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='Input filename template, use $1 for params, $2 for data types as wildcard')
    parser.add_argument('-p', '--parameters', dest='params', nargs='+', help='Parameter space')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    for param in args.params:
        filename = args.filename.replace('$1', param)
        logger.debug('Base filename: ' + str(filename))

        dmp = pd.read_pickle(filename.replace('$2', 'dmp'))
        rm = pd.read_pickle(filename.replace('$2', 'rm'))
        sink = pd.read_pickle(filename.replace('$2', 'sink'))

