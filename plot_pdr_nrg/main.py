#!/bin/python3

import math
import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np


def sum_list_prop(list_prop):
    return [sum([x[list_prop] for x in i['nodes']]) for i in loader['nrg_list']]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_pdr_nrg', description='Plot network pdr and energy over time', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin', nargs='+')
    parser.add_argument('-e', '--event', dest='event', type=int)

    args = parser.parse_args()

    files = args.filename

    total_nrg_arr = {}
    eff_nrg_arr = {}
    timestamp = {}

    for file in files:
        stream = open(file, 'r')

        loader = yaml.safe_load(stream)

        sent_t_arr = sum_list_prop('report_sent')
        recv_t_arr = sum_list_prop('report_recv')
        nrg_t_arr = sum_list_prop('energy')

        sent_d_arr = np.subtract(sent_t_arr[1:], sent_t_arr[:-1])
        recv_d_arr = np.subtract(recv_t_arr[1:], recv_t_arr[:-1])
        nrg_d_arr = np.subtract(nrg_t_arr[:-1], nrg_t_arr[1:])

        timestamp[file] = [round(i['timestamp'], 0) for i in loader['nrg_list']][:-1]

        pdr_arr = np.divide(recv_d_arr, sent_d_arr)
        nrg_eff_arr = np.multiply(pdr_arr, nrg_d_arr)

        total_nrg_arr[file] = nrg_d_arr
        eff_nrg_arr[file] = nrg_eff_arr

    rows = 2
    columns = math.ceil(len(files)/2)
    idx = 0

    max_val = max([max(i) for i in total_nrg_arr.values()])

    for idx, file in enumerate(files):
        plt.subplot(rows, columns, idx+1)
        plt.plot(timestamp[file], np.transpose(np.array([eff_nrg_arr[file], total_nrg_arr[file]])))
        plt.ylim(top=math.ceil(max_val))
        if args.event is not None:
            plt.axvline(x=args.event, color='r')
        plt.grid(True)
        plt.title(file.split('/')[-1])
    plt.legend(['Efficient energy consumed', 'Total energy consumed'])

    plt.show()

