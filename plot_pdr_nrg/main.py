#!/bin/python3

import math
import yaml
import argparse
import matplotlib.pyplot as plt
import sys
import numpy as np
import matplotlib as mpl


def sum_list_prop(list_prop):
    return [sum([x[list_prop] for x in i['nodes']]) for i in loader['nrg_list']]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_pdr_nrg', description='Plot network pdr and energy over time', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin', nargs='+')
    parser.add_argument('-e', '--event', dest='event', type=int)
    parser.add_argument('-l', '--labels', dest='labels', type=str, nargs='+')
    parser.add_argument('-c','--correction', dest='corr', type=int, default=20, help='Correct Watts if period is not 1 sec, and it is not 1 sec usually')

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

        total_nrg_arr[file] = np.divide(nrg_d_arr, args.corr)
        eff_nrg_arr[file] = np.divide(nrg_eff_arr, args.corr)

    rows = 2
    columns = math.ceil(len(files)/2)
    idx = 0

    max_val = max([max(i) for i in total_nrg_arr.values()])
    fig = plt.figure(figsize=(5, 5))
    axes = fig.subplots(rows, columns)

    #axes = fig.subplot_mosaic('ab;cd;ee')

    ax = axes.ravel()
    #ax = list(axes.values())
    for idx, file in enumerate(files):
        ax[idx].plot(timestamp[file], np.transpose(np.array([eff_nrg_arr[file], total_nrg_arr[file]])))
        ax[idx].set_ylim(top=math.ceil(max_val), bottom=0)

        start, end = ax[idx].get_ylim()
        ax[idx].yaxis.set_ticks(np.arange(start, end, 0.5))

        if args.event is not None:
            plt.axvline(x=args.event, color='r')
        ax[idx].grid(True)
        ax[idx].set_title(args.labels[idx], loc='left')
        ax[idx].set_xlabel('Time (s)')
#        plt.ylabel(r'$\frac{J}{h}$')
        ax[idx].set_ylabel('Energy (W)')
        ax[idx].margins(x=0.01, y=0.01)
    plt.legend(['Efficient energy consumed', 'Total energy consumed'], loc='upper center', ncol=2, bbox_to_anchor=(-0.15, -0.3))
    #plt.legend(['Efficient energy consumed', 'Total energy consumed'], ncol=2)
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
    #          fancybox=True, shadow=True, ncol=5)
    #fig.tight_layout()
    plt.show()

