#!/bin/env python3

import logging
logger = logging.getLogger(__name__)
import yaml
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np

def calculate_chebyshev(arr):
    return np.sum(np.power(arr, 2))**2/ ( len(arr)* np.sum(np.power(arr, 4)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pick_border', description='Pick a border node', epilog=':-(')
    parser.add_argument('-t', '--topsis', dest='topsis_files', help='Topsis results loc_pdr', nargs='+')
    parser.add_argument('-r', '--rnd', dest='rnd_files', help='RND results loc_pdr', nargs='+')
    parser.add_argument('-b', '--borders', dest='borders', help='Border nodes in question', nargs='*', type=int)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    if len(args.topsis_files) != len(args.rnd_files):
        logger.error('Number of files for each type of data must mach')

    file_pairs = zip(args.topsis_files, args.rnd_files)

    topsis_c_arr = []
    rnd_c_arr = []

    topsis_b_arr = []
    rnd_b_arr = []


    for f_idx, files in enumerate(file_pairs):
        stream = open(files[0], 'r')
        loader = yaml.safe_load(stream)
        border_nrg = [ i['spent_energy'] for i in loader if 'border' in [j['role'] for j in i['engines'] ] ]
        topsis_c_arr.append(calculate_chebyshev(border_nrg))

        if args.borders:
            border_nrg = [i['spent_energy'] for i in loader if 'border' in [j['role'] for j in i['engines']] and i['node'] == args.borders[f_idx]]
            topsis_b_arr.append(sum(border_nrg))

        stream = open(files[1], 'r')
        loader = yaml.safe_load(stream)
        border_nrg = [ i['spent_energy'] for i in loader if 'border' in [j['role'] for j in i['engines'] ] ]
        rnd_c_arr.append(calculate_chebyshev(border_nrg))

        if args.borders:
            border_nrg = [i['spent_energy'] for i in loader if
                          'border' in [j['role'] for j in i['engines']] and i['node'] == args.borders[f_idx]]
            rnd_b_arr.append(sum(border_nrg))

    if args.borders:
        nrows=2
    else:
        nrows=1

    fig, axs = plt.subplots(nrows=nrows, ncols=1, layout='compressed', figsize=(8,16))
    axs_arr = axs.ravel()

    axs_arr[0].plot(rnd_c_arr,topsis_c_arr, 'o')
    axs_arr[0].set_xlabel('RND C-sum')
    axs_arr[0].set_ylabel('TOPSIS C-sum')


    if args.borders:
        axs_arr[1].plot(rnd_b_arr, topsis_b_arr, 'o')
        axs_arr[1].set_xlabel('RND B node')
        axs_arr[1].set_ylabel('TOPSIS B node')

    fig.savefig('plot.pdf', bbox_inches='tight')

